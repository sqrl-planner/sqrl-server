from typing import Any, Optional

import graphene
from graphene_mongo import MongoengineObjectType
import mongoengine
from flask import current_app

from sqrl.models.common import Time
from sqrl.models.timetable import (
    SectionMeeting,
    Instructor,
    Section,
    Organisation,
    Course,
    Timetable,
)


class _TimeObject(MongoengineObjectType):
    """A time object in the graphql schema."""

    class Meta:
        model = Time


class _SectionMeetingObject(MongoengineObjectType):
    """A section meeting in the graphql schema."""

    class Meta:
        model = SectionMeeting


class _InstructorObject(MongoengineObjectType):
    """An instructor in the graphql schema."""

    class Meta:
        model = Instructor


class _SectionObject(MongoengineObjectType):
    """A section in the graphql schema."""

    class Meta:
        model = Section

    code = graphene.String()

    def resolve_code(self, info: graphene.ResolveInfo, **kwargs: Any) -> str:
        """Resolve the code of the section."""
        return self.code


class _OrganisationObject(MongoengineObjectType):
    """An organisation in the graphql schema."""

    class Meta:
        model = Organisation


class _OrganisationObjectConnection(graphene.relay.Connection):
    """A connection for the Organisation object."""

    class Meta:
        node = _OrganisationObject


class _CourseObject(MongoengineObjectType):
    """A course in the graphql schema."""

    class Meta:
        model = Course


class _CourseObjectConnection(graphene.relay.Connection):
    """A connection for the Course object."""

    class Meta:
        node = _CourseObject


class _TimetableObject(MongoengineObjectType):
    """A timetable in the graphql schema."""

    class Meta:
        model = Timetable
        exclude_fields = ('key',)


class Query(graphene.ObjectType):
    """A query in the graphql schema."""

    organisation_by_code = graphene.Field(
        _OrganisationObject, code=graphene.String(required=True)
    )
    organisations = graphene.ConnectionField(_OrganisationObjectConnection)

    courses_by_id = graphene.List(
        _CourseObject, ids=graphene.NonNull(graphene.List(graphene.NonNull(graphene.String))))
    course_by_id = graphene.Field(
        _CourseObject, id=graphene.String(required=True))
    courses = graphene.ConnectionField(_CourseObjectConnection)
    search_courses = graphene.List(
        _CourseObject,
        query=graphene.String(required=True),
        offset=graphene.Int(required=False, default_value=0),
        limit=graphene.Int(required=False, default_value=25),
    )

    timetable_by_id = graphene.Field(
        _TimetableObject, id=graphene.ID(required=True))

    def resolve_organisation_by_code(
        self, info: graphene.ResolveInfo, code: str
    ) -> Organisation:
        """Return an _OrganisationObject object with the given code."""
        return Organisation.objects.get(code=code)

    def resolve_organisations(
        self, info: graphene.ResolveInfo, **kwargs: Any
    ) -> list[Organisation]:
        """Return a list of _OrganisationObject objects."""
        return list(Organisation.objects.all())

    def resolve_courses_by_id(
            self, info: graphene.ResolveInfo, ids: list[str]) -> list[Course]:
        """Return a list of _CourseObject objects, each with given ids.
        Courses that do not exist are null.
        """
        courses = []
        for id in ids:
            try:
                course = Course.objects.get(id=id)
                courses.append(course)
            except mongoengine.DoesNotExist:
                courses.append(None)
        return courses

    def resolve_course_by_id(
            self, info: graphene.ResolveInfo, id: str) -> Course:
        """Return a _CourseObject object with the given id."""
        return Course.objects.get(id=id)

    def resolve_courses(self, info: graphene.ResolveInfo,
                        **kwargs: Any) -> list[Course]:
        """Return a list of _CourseObject objects."""
        return list(Course.objects.all())

    def resolve_search_courses(
        self, info: graphene.ResolveInfo, query: str, offset: int, limit: int
    ) -> list[Course]:
        """Return a list of _CourseObject objects matching the given search string."""
        # log search query
        current_app.logger.info(f'searchCourses - query: "{query}", '
                                f'offset: {offset}, limit: {limit}')

        courses_code = Course.objects(code__icontains=query)
        # First n search results
        n = courses_code.count()
        if offset < n:
            courses = list(courses_code[offset: offset + limit])
            if limit > n - offset:
                courses_text = Course.objects.search_text(
                    query).order_by('$text_score')
                courses += list(courses_text.limit(limit - n + offset))
            return courses
        else:
            courses = Course.objects.search_text(query).order_by('$text_score')
            offset -= n
            return list(courses[offset: offset + limit])

    def resolve_timetable_by_id(
            self, _: graphene.ResolveInfo, id: str) -> Timetable:
        """Return a Timetable object with the given id."""
        return Timetable.objects.get(id=id)


class CreateTimetableMutation(graphene.Mutation):
    """Create timetable mutation in the graphql schema."""

    class Arguments:
        name = graphene.String(required=False, default_value=None)

    timetable = graphene.Field(_TimetableObject)
    key = graphene.String()

    def mutate(
        self, info: graphene.ResolveInfo, name: Optional[str] = None
    ) -> 'CreateTimetableMutation':
        """Create a timetable."""
        timetable = Timetable()
        if name is not None:
            timetable.name = name
        timetable.save()
        return CreateTimetableMutation(timetable=timetable, key=timetable.key)


class DeleteTimetableMutation(graphene.Mutation):
    """Delete timetable mutation in the graphql schema."""

    class Arguments:
        id = graphene.ID(required=True)
        key = graphene.String(required=True)

    timetable = graphene.Field(_TimetableObject)

    def mutate(
        self, _: graphene.ResolveInfo, id: str, key: str
    ) -> 'DeleteTimetableMutation':
        """Delete a timetable."""
        timetable = Timetable.objects.get(id=id)
        if timetable is None:
            raise Exception(f'could not find timetable with id "{id}"')

        if timetable.key != key:
            raise Exception('the provided timetable key did not match')

        timetable.delete()
        return DeleteTimetableMutation(timetable=timetable)


class AddSectionsTimetableMutation(graphene.Mutation):
    """Add sections to timetable mutation in the graphql schema."""

    class Arguments:
        id = graphene.ID(required=True)
        key = graphene.String(required=True)
        course_id = graphene.String(required=True)
        sections = graphene.List(graphene.String, required=True)

    timetable = graphene.Field(_TimetableObject)

    def mutate(
        self,
        _: graphene.ResolveInfo,
        id: str,
        key: str,
        course_id: str,
        sections: list[str],
    ) -> 'AddSectionsTimetableMutation':
        """Add sections to a timetable."""
        timetable = Timetable.objects.get(id=id)
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
        id = graphene.ID(required=True)
        key = graphene.String(required=True)
        course_id = graphene.String(required=True)
        sections = graphene.List(graphene.String, required=True)

    timetable = graphene.Field(_TimetableObject)

    def mutate(
        self,
        _: graphene.ResolveInfo,
        id: str,
        key: str,
        course_id: str,
        sections: list[str],
    ) -> 'SetSectionsTimetableMutation':
        """Set sections in a timetable. If a section of the same type for the
        given course exists in the timetable, then it is removed and replaced
        with the new one.
        """
        timetable = Timetable.objects.get(id=id)
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


class Mutation(graphene.ObjectType):
    """Mutations in the graphql schema."""

    create_timetable = CreateTimetableMutation.Field()
    delete_timetable = DeleteTimetableMutation.Field()
    add_sections_timetable = AddSectionsTimetableMutation.Field()
    set_sections_timetable = SetSectionsTimetableMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
