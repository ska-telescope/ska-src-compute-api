from distutils.util import strtobool
import json

from fastapi_app.common.exceptions import MissingPermissionKeyword, NoPermissionDefinitionForRoute, \
    PermissionDenied, PermissionExpressionMalformed


class Permission:
    def __init__(self, permissions_definition_path, roles_definition_path, root_group="fastapi_app"):
        self.root_group = root_group

        # Open permissions definition and parse.
        with open(permissions_definition_path, 'r') as f:
            self.permissions_definition = json.load(f)

        # Open roles definition and parse.
        with open(roles_definition_path, 'r') as f:
            self.roles_definition = json.load(f)

    def _check_group_membership_for_role(self, role_expression, groups, **kwargs):
        required_role_groups = self.roles_definition[role_expression]
        for required_role_group in required_role_groups:
            try:
                if required_role_group.format(root_group=self.root_group, **kwargs) in groups:
                    return True
                return False
            except KeyError as e:
                raise MissingPermissionKeyword(repr(e.args))
        return True

    def check_role_membership_for_route(self, route, method, groups, **kwargs):
        evaluated_permission_expression = []            # list to store all the different clauses in a permission expr
        if route in self.permissions_definition:
            if method in self.permissions_definition[route]:
                role_expression = str(self.permissions_definition[route][method])
                for role_expression_token in role_expression.split():
                    role_expression_token = role_expression_token.strip().rstrip('/')
                    if role_expression_token in self.roles_definition:
                        evaluated_permission_expression.append(
                            str(self._check_group_membership_for_role(
                                role_expression=role_expression_token, groups=groups, **kwargs)))
                    elif role_expression_token.lower() in ['and', 'or', 'not']:
                        evaluated_permission_expression.append(role_expression_token)
                    elif role_expression_token.lower() in ['true', 'false']:
                        evaluated_permission_expression.append(str(strtobool(role_expression_token)))
                    else:
                        raise PermissionExpressionMalformed(role_expression)
                try:
                    has_permission = eval(' '.join(evaluated_permission_expression))
                except (NameError, SyntaxError):
                    raise PermissionExpressionMalformed(evaluated_permission_expression)
                if not has_permission:
                    raise PermissionDenied
                return True
            raise NoPermissionDefinitionForRoute
        raise NoPermissionDefinitionForRoute
