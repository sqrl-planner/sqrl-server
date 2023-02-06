"""Orgaisation query (proxied from Gator API)."""
from typing import Any
from types import SimpleNamespace

import graphene
from gator.core.models.timetable import Organisation

from sqrl.extensions.gator_client import gator_client
from sqrl.graphql.objects import OrganisationObject, PaginatedOrganisationsObject


class OrganisationQuery(graphene.ObjectType):
    """Organisation related queries."""

    organisation_by_code = graphene.Field(
        OrganisationObject, code=graphene.String(required=True)
    )
    organisations = graphene.Field(PaginatedOrganisationsObject)

    def resolve_organisation_by_code(
        self, info: graphene.ResolveInfo, code: str
    ) -> Organisation:
        """Return an Organisation with the given code."""
        return gator_client.get_organisation(code)

    def resolve_organisations(
        self, info: graphene.ResolveInfo, **kwargs: Any
    ) -> SimpleNamespace:
        """Return a paginated list of Organisations."""
        return gator_client.get_organisations()
