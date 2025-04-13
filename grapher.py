import math
from matplotlib.widgets import Slider
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

from drone import Drone
import utils

MAX_SIM_TIME = 5000

def drawFlightPath(lander : Drone):
    def on_hover(event):
        if event.inaxes == data_axis:  # Check if cursor is inside the plot area
            closest_index = np.argmin(np.abs(time - event.xdata))  # Find closest X index
            time_val, alt_val = time[closest_index], altitude[closest_index]
            hs_val = hs[closest_index]
            vs_val = vs[closest_index]
            rotation_val = rotation[closest_index]
            fuel_val = fuel[closest_index]
            thrust_val = thrust[closest_index]
            mass_val = mass[closest_index]

            speed_val = math.sqrt(hs_val ** 2 + vs_val ** 2)

            # Update text position and content
            text.set_position((event.xdata, event.ydata))
            text.set_text(f"Time: {time_val:.2f}\nAltitude: {alt_val:.2f}\nHS: {hs_val:.2f} " + \
                          f"\nVS: {vs_val:.2f}\nSpeed: {speed_val:.2f}\nRotation: {rotation_val:.2f}"
                          f"\nFuel: {fuel_val:.2f}\nTrust: {thrust_val:.2f}\nMass: {mass_val:.2f}")
            fig.canvas.draw_idle()  # Redraw the figure

    def update(val):
        lander.reset()

        for i, data in enumerate(lander.getEditableProperties()):
            _, propertyname, _, _, _ = data
            new_value = sliders[i].val
            lander.setData(propertyname, new_value)

        nonlocal time, altitude, hs, vs, rotation, fuel, thrust, mass
        time, altitude, hs, vs, rotation, fuel, thrust, mass = lander.getFullFlightPath(1, MAX_SIM_TIME)

        alt_line.set_xdata(time)
        thrust_line.set_xdata(time)
        horizontal_line.set_xdata(time)
        vertical_line.set_xdata(time)
        fuel_line.set_xdata(time)
        weight_line.set_xdata(time)
        
        alt_line.set_ydata(altitude)
        thrust_line.set_ydata(thrust)
        horizontal_line.set_ydata(hs)
        vertical_line.set_ydata(vs)
        fuel_line.set_ydata(fuel)
        weight_line.set_ydata(mass)

        for i, row in enumerate(axs):
            for j, cell in enumerate(row):
                cell.relim()
                cell.autoscale_view()

        fig.canvas.draw_idle()

    fig, axs = plt.subplots(3, 2)
    data_axis = axs[0, 0]
    thrust_axis = axs[1, 0]
    horizontal_axis = axs[0, 1]
    vertical_axis = axs[1, 1]
    fuel_axis = axs[2, 0]
    weight_axis = axs[2, 1]

    data_axis.set_title('Full Landing Data')
    thrust_axis.set_title('Thrust')
    horizontal_axis.set_title('Horizontal Speed')
    vertical_axis.set_title('Vertical Speed')
    fuel_axis.set_title('Fuel')
    weight_axis.set_title('Weight')

    fig.subplots_adjust(wspace=0.1, hspace=0.4)

    labels = [
        [('Time', 'Altitude'), ('Time', 'Thrust')],
        [('Time', 'Mps'), ('Time', 'Mps')],
        [('Time', 'Liter'), ('Time', 'Kg')],
    ]
    for i, row in enumerate(axs):
        for j, cell in enumerate(row):
            (xtext, ytext) = labels[i][j]

            cell.set_xlabel(xtext)
            cell.set_ylabel(ytext)


    plt.legend()
    plt.subplots_adjust(left=0.05, top=0.95, bottom=0.25, right= 0.98)  # Space for sliders

    text = data_axis.text(0, 0, "", fontsize=10, color="red", bbox=dict(facecolor="white", alpha=0.7))

    time, altitude, hs, vs, rotation, fuel, thrust, mass = all_data = lander.getFullFlightPath(1, MAX_SIM_TIME)

    utils.export(all_data)

    alt_line, = data_axis.plot(time, altitude, 'b-', label="Landing Path")
    thrust_line, = thrust_axis.plot(time, thrust, 'b-', label="Thrust")
    horizontal_line, = horizontal_axis.plot(time, hs, 'b-', label="Horizontal Speed")
    vertical_line, = vertical_axis.plot(time, vs, 'b-', label="Vertical Speed")
    fuel_line, = fuel_axis.plot(time, fuel, 'b-', label="Fuel")
    weight_line, = weight_axis.plot(time, mass, 'b-', label="Weight")
    lander.reset()

    fig.canvas.mpl_connect("motion_notify_event", on_hover)

    # Add sliders
    sliders : list[Slider] = []
    for i, data in enumerate(lander.getEditableProperties()):
        slidername, propertyname, minvalue, startvalue, maxvalue= data

        axis = plt.axes([0.3, 0.02 + i * 0.03, 0.4, 0.03])
        slider = Slider(axis, slidername, minvalue, maxvalue, startvalue)
        slider.on_changed(update)
        sliders.append(slider)

    plt.show()