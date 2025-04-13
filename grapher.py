import math
from matplotlib.widgets import Slider
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

from drone import Drone

MAX_SIM_TIME = 5000

def drawFlightPath(lander : Drone):
    def on_hover(event):
        if event.inaxes == ax:  # Check if cursor is inside the plot area
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

        line.set_xdata(time)
        line.set_ydata(altitude)

        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()


    fig, ax = plt.subplots()
    plt.xlabel("Time (s)")
    plt.ylabel("Altitude (m)")
    plt.title("Ship Landing Simulation")
    plt.legend()
    plt.subplots_adjust(left=0.15, bottom=0.50)  # Space for sliders

    text = ax.text(0, 0, "", fontsize=10, color="red", bbox=dict(facecolor="white", alpha=0.7))

    time, altitude, hs, vs, rotation, fuel, thrust, mass = lander.getFullFlightPath(1, MAX_SIM_TIME)
    line, = plt.plot(time, altitude, 'b-', label="Landing Path")
    lander.reset()

    fig.canvas.mpl_connect("motion_notify_event", on_hover)

    # Add sliders
    sliders : list[Slider] = []
    for i, data in enumerate(lander.getEditableProperties()):
        slidername, propertyname, minvalue, startvalue, maxvalue= data

        axis = plt.axes([0.3, 0.1 + i * 0.05, 0.5, 0.03])
        slider = Slider(axis, slidername, minvalue, maxvalue, startvalue)
        slider.on_changed(update)
        sliders.append(slider)

    print(max(altitude))
    plt.show()