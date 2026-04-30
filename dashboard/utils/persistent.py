from dash.development.base_component import Component

def make_persistent(component: Component) -> Component:
    """
    Tự động thêm thuộc tính persistence vào bất kỳ component nào được truyền vào.
    
    Args:
        component (Component): Một component của Dash (Input, Dropdown, RadioItems...)
        
    Returns:
        Component: Component đã được cấu hình tính năng ghi nhớ.
    """
    component.persistence = True
    component.persistence_type = 'session'
    component.persisted_props = ['value']
    return component
