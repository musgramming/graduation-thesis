from dash.development.base_component import Component


def make_persistent(component: Component) -> Component:
    component.persistence = True
    component.persistence_type = "session"
    component.persisted_props = ["value"]
    return component