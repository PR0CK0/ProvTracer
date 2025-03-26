import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(label="Example", width=600, height=400):
    dpg.add_button(label="Click Me")

dpg.create_viewport(title="Scalable UI", width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
