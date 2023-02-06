"""Timetable queries and mutations."""
from typing import Optional

import graphene
from gator.core.models.timetable import Course

from sqrl.graphql.objects import UserTimetableObject
from sqrl.models import UserTimetable


class TimetableQuery(graphene.ObjectType):
    """Timetable queries in the graphql schema."""

    timetable_by_id = graphene.Field(
        UserTimetableObject, id=graphene.ID(required=True))

    def resolve_timetable_by_id(
        self, info: graphene.ResolveInfo, id: str
    ) -> Optional[UserTimetable]:
        """Return a UserTimetable object with the given id."""
        timetable = UserTimetable.objects.get(id=id)
        if timetable is None or timetable.deleted:
            return None
        else:
            return timetable


class SetTimetableNameMutation(graphene.Mutation):
    """Create timetable mutation in the graphql schema."""

    class Arguments:
        """Arguments for the mutation.

        Instance Attributes:
            id: The id of the timetable to set the name of.
            key: A private key to verify the user has permission to set the name.
            name: The new name of the timetable.
        """
        id = graphene.ID(required=True)
        key = graphene.String(required=True)
        name = graphene.String(required=True, default_value=None)

    timetable = graphene.Field(UserTimetableObject)
    key = graphene.String()

    def mutate(
        self,
        _: graphene.ResolveInfo,
        id: str,
        key: str,
        name: str,
    ) -> 'SetTimetableNameMutation':
        """Set a timetable's name."""
        timetable = UserTimetable.objects.get(id=id)
        if timetable is None:
            raise Exception(f'could not find timetable with id "{id}"')

        if timetable.key != key:
            raise Exception('the provided timetable key did not match')

        timetable.name = name

        timetable.save()
        return SetTimetableNameMutation(timetable=timetable)


class CreateTimetableMutation(graphene.Mutation):
    """Create timetable mutation in the graphql schema."""

    class Arguments:
        """Arguments for the mutation.

        Instance Attributes:
            name: The name of the new timetable.
        """
        name = graphene.String(required=False, default_value=None)

    timetable = graphene.Field(UserTimetableObject)
    key = graphene.String()

    def mutate(
        self, info: graphene.ResolveInfo, name: Optional[str] = None
    ) -> 'CreateTimetableMutation':
        """Create a timetable."""
        timetable = UserTimetable()
        if name is not None:
            timetable.name = name
        timetable.save()
        return CreateTimetableMutation(timetable=timetable, key=timetable.key)


class DuplicateTimetableMutation(graphene.Mutation):
    """Delete timetable mutation in the graphql schema."""

    class Arguments:
        """Arguments for the mutation.

        Instance Attributes:
            id: The id of the timetable to duplicate.
            name: The name of the new timetable.
        """
        id = graphene.ID(required=True)
        name = graphene.String(required=False, default_value=None)

    timetable = graphene.Field(UserTimetableObject)
    key = graphene.String()

    def mutate(
            self, info: graphene.ResolveInfo, id: str, name: Optional[str] = None
    ) -> 'DuplicateTimetableMutation':
        """Duplicate a timetable."""
        timetable = UserTimetable.objects.get(id=id)
        if timetable is None:
            raise Exception(f'could not find timetable with id "{id}"')

        next_timetable = UserTimetable()
        if name is not None:
            next_timetable.name = name

        next_timetable.sections = timetable.sections
        next_timetable.name = f'Copy of {timetable.name}'

        next_timetable.save()

        return DuplicateTimetableMutation(timetable=next_timetable, key=next_timetable.key)


class DeleteTimetableMutation(graphene.Mutation):
    """Delete timetable mutation in the graphql schema."""

    class Arguments:
        """Arguments for the mutation.

        Instance Attributes:
            id: The id of the timetable to delete.
            key: The private key to authorize the deletion.
        """
        id = graphene.ID(required=True)
        key = graphene.String(required=True)

    timetable = graphene.Field(UserTimetableObject)

    def mutate(
        self, _: graphene.ResolveInfo, id: str, key: str
    ) -> 'DeleteTimetableMutation':
        """Delete a timetable."""
        timetable = UserTimetable.objects.get(id=id)
        if timetable is None:
            raise Exception(f'could not find timetable with id "{id}"')

        if timetable.key != key:
            raise Exception('the provided timetable key did not match')

        timetable.delete()
        return DeleteTimetableMutation(timetable=timetable)


class RemoveCourseTimetableMutation(graphene.Mutation):
    """Remove course from timetable mutation in the graphql schema."""

    class Arguments:
        """Arguments for the mutation.

        Instance Attributes:
            id: The id of the timetable to remove the course from.
            key: The key of the timetable to remove the course from.
            course_id: The id of the course to remove from the timetable.
        """
        id = graphene.ID(required=True)
        key = graphene.String(required=True)
        course_id = graphene.String(required=True)

    timetable = graphene.Field(UserTimetableObject)

    def mutate(
        self,
        _: graphene.ResolveInfo,
        id: str,
        key: str,
        course_id: str,
    ) -> 'RemoveCourseTimetableMutation':
        """Remove course from a timetable."""
        timetable = UserTimetable.objects.get(id=id)
        if timetable is None:
            raise Exception(f'could not find timetable with id "{id}"')

        if timetable.key != key:
            raise Exception('the provided timetable key did not match')

        if course_id not in timetable.sections:
            timetable.sections[course_id] = []

        timetable.sections.pop(course_id)

        timetable.save()
        return RemoveCourseTimetableMutation(timetable=timetable)


class AddSectionsTimetableMutation(graphene.Mutation):
    """Add sections to timetable mutation in the graphql schema."""

    class Arguments:
        """Arguments for the mutation.

        Instance Attributes:
            id: The id of the timetable to add the sections to.
            key: A private key to authorize adding sections to the timetable.
            course_id: The id of the course to add the sections to.
            sections: The sections to add to the course.
        """
        id = graphene.ID(required=True)
        key = graphene.String(required=True)
        course_id = graphene.String(required=True)
        sections = graphene.List(graphene.String, required=True)

    timetable = graphene.Field(UserTimetableObject)

    def mutate(
        self,
        _: graphene.ResolveInfo,
        id: str,
        key: str,
        course_id: str,
        sections: list[str],
    ) -> 'AddSectionsTimetableMutation':
        """Add sections to a timetable."""
        timetable = UserTimetable.objects.get(id=id)
        if timetable is None:
            raise Exception(f'could not find timetable with id "{id}"')

        if timetable.key != key:
            raise Exception('the provided timetable key did not match')

        course = Course.objects.get(id=course_id)
        if course is None:
            raise Exception(f'could not find course with id "{course_id}"')

        if course_id not in timetable.sections:
            timetable.sections[course_id] = []

        for section in sections:
            if section not in course.section_codes:
                raise Exception(
                    f'could not find section with code "{section}"')
            else:
                timetable.sections[course_id].append(section)

        timetable.save()
        return AddSectionsTimetableMutation(timetable=timetable)


class SetSectionsTimetableMutation(graphene.Mutation):
    """Set sections in timetable mutation in the graphql schema."""

    class Arguments:
        """Arguments for the mutation.

        Instance Attributes:
            id: The id of the timetable to set the sections in.
            key: A private key to authorize setting sections in the timetable.
            course_id: The id of the course to set the sections in.
            sections: The sections to set in the course.
        """
        id = graphene.ID(required=True)
        key = graphene.String(required=True)
        course_id = graphene.String(required=True)
        sections = graphene.List(graphene.String, required=True)

    timetable = graphene.Field(UserTimetableObject)

    def mutate(
        self,
        _: graphene.ResolveInfo,
        id: str,
        key: str,
        course_id: str,
        sections: list[str],
    ) -> 'SetSectionsTimetableMutation':
        """Set sections in a timetable.

        If a section of the same type for the given course exists in the
        timetable, then it is removed and replaced with the new one.
        """
        timetable = UserTimetable.objects.get(id=id)
        if timetable is None:
            raise Exception(f'could not find timetable with id "{id}"')

        if timetable.key != key:
            raise Exception('the provided timetable key did not match')

        course = Course.objects.get(id=course_id)
        if course is None:
            raise Exception(f'could not find course with id "{course_id}"')

        if course_id not in timetable.sections:
            timetable.sections[course_id] = []

        teaching_methods_to_remove = set()
        for section_code in sections:
            if section_code not in course.section_codes:
                raise Exception(
                    f'could not find section with code "{section_code}"')
            else:
                teaching_methods_to_remove.add(section_code.split('-')[0])

        # Clean old sections
        old_sections = timetable.sections[course_id]
        for i in range(len(old_sections) - 1, -1, -1):
            # Extract teaching method and check if it needs to be removed
            old_teaching_method = old_sections[i].split('-')[0]
            if old_teaching_method in teaching_methods_to_remove:
                # Remove old section from timetable since it is the same type
                # as a new one
                timetable.sections[course_id].pop(i)

        # Add new sections
        for section_code in sections:
            timetable.sections[course_id].append(section_code)

        timetable.save()
        return SetSectionsTimetableMutation(timetable=timetable)


class TimetableMutation(graphene.ObjectType):
    """Timetable mutations in the graphql schema."""

    create_timetable = CreateTimetableMutation.Field()
    set_timetable_name = SetTimetableNameMutation.Field()
    delete_timetable = DeleteTimetableMutation.Field()
    duplicate_timetable = DuplicateTimetableMutation.Field()
    remove_course_timetable = RemoveCourseTimetableMutation.Field()
    add_sections_timetable = AddSectionsTimetableMutation.Field()
    set_sections_timetable = SetSectionsTimetableMutation.Field()
