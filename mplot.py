#!/usr/bin/env python

###############################################
#
# mplot - manipulate parameters of function
# writen by Xusheng Xu (thuxuxs@gmail.com)
#
###############################################

import numpy as np
from scipy.integrate import ode
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
import pandas as pd
import sys
v=3 if sys.version>'2' else 2

class mplot:
    """
    Xusheng Xu, thuxuxs@gmail.com

    totally control the function you want to show by the parameters

    usage
    ------

    def generate(x, a, phi):
        out = np.array([x, a * np.sin(x + phi), a * np.cos(x + phi)]).T
        return pd.DataFrame(out, columns=['x', 'sin', 'cos'])

    fig = mplot(generate, np.linspace(0, 10, 100), a=(1, 2), phi=(0, 2 * np.pi))

    # usage 1
    # sub1 = fig.add_subplot(121)
    # fig.add_line(sub1, 'x', 'sin', 'r', linewidth=2, label='sin')
    # fig.add_line(sub1, 'x', 'cos', 'k-.', lw=4, label='cos')
    # sub2 = fig.add_subplot(122)
    # fig.add_line(sub2, 'sin', 'cos')

    # usage 2
    fig.add_subplot()
    fig.add_all()
    fig.show()
    """
    def __init__(self, func, x, **kwargs):
        self.bottom = 0.08
        self.slider_width = 0.8
        self.slider_height = 0.04

        self.func = func
        self.x = x
        self.kwargs = kwargs
        self.arg_num = len(self.kwargs)
        if v==2:
            self.parameter = {name: (high + low) / 2.0 for name, (low, high) in self.kwargs.iteritems()}
        else:
            self.parameter = {name: (high + low) / 2.0 for name, (low, high) in self.kwargs.items()}
        self.func_init = self.func(self.x, **self.parameter)

        self.fig = plt.figure()
        self.sub = []
        self.lines = []
        self.sliders = {}

    def add_subplot(self, poi=111):
        """

        :param poi: position of the figure
        """
        self.sub.append(self.fig.add_subplot(poi))
        return self.sub[-1]

    def add_line(self, sub, x_axis, y_axis, *args, **kwargs):
        """
        add a line to a certain subplot

        :param sub: subplot
        :param x_axis: x axis name
        :param y_axis: y axis name
        :param args: line style for plot
        :param kwargs: line style for plot
        """
        line = sub.plot(self.func_init[x_axis], self.func_init[y_axis], *args, **kwargs)[0]
        self.lines.append({'x': x_axis, 'y': y_axis, 'line': line})
        plt.legend()

    def add_all(self, sub=None):
        """
        add all lines to one subplot
        :param sub: subplot
        """
        if sub is None:
            sub = self.sub[-1]
        x_axis = self.func_init.columns[0]
        for y_axis in self.func_init.columns[1:]:
            line = sub.plot(self.func_init[x_axis], self.func_init[y_axis])[0]
            self.lines.append({'x': x_axis, 'y': y_axis, 'line': line})
            plt.legend()

    def show(self):
        self.fig.subplots_adjust(bottom=self.bottom + self.arg_num * self.slider_height)
        if v==2:
            for index, (name, (low, high)) in enumerate(self.kwargs.iteritems()):
                self.sliders[name] = Slider(plt.axes(
                    [0.1, index * self.slider_height + self.bottom / 2.0, self.slider_width, self.slider_height * 0.8]),
                    name, low, high, valinit=self.parameter[name])
                self.sliders[name].on_changed(self.update(name))
        else:
            for index, (name, (low, high)) in enumerate(self.kwargs.items()):
                self.sliders[name] = Slider(plt.axes(
                    [0.1, index * self.slider_height + self.bottom / 2.0, self.slider_width, self.slider_height * 0.8]),
                    name, low, high, valinit=self.parameter[name])
                self.sliders[name].on_changed(self.update(name))
        plt.show()

    def update(self, *name):
        name, = name

        def update_real(val):
            self.parameter[name] = val
            self.func_on_changed = self.func(self.x, **self.parameter)
            for line in self.lines:
                line['line'].set_xdata(self.func_on_changed[line['x']])
                line['line'].set_ydata(self.func_on_changed[line['y']])

            for i in self.sub:
                i.relim()
                i.autoscale_view()

            self.fig.canvas.draw()

        return update_real

    
def dsolve(f, t, parameters, init, result_handle=lambda x: x,integrator='zvode'):
    """
    Xusheng Xu, thuxuxs@gmail.com

    Solve differential equations!

    usage
    ------
    def f(t,y,args):
        omega,kappa=[args[i] for i in ['omega','kappa']]
        a=y[0]
        return [np.cos(omega*t)*np.exp(-kappa*t)*omega]
    t=np.arange(0,100,0.1).reshape((-1,1))
    parameters={'omega':(0,10),
                'kappa':(0,0.1)}
    init=[[['y'],[0]],['t',0]]
    def result_handle(out):
        out['y']=out['y']**2
        return out
    dsolve(f,t,parameters,init,result_handle)
    """

    dt = t[1, 0] - t[0, 0]
    t1 = t[-1, 0]
    y0 = init[0][1]
    t0 = init[1][1]
    col = [init[1][0]]
    col.extend(init[0][0])

    def generate(t, **parameters):
        r = ode(f).set_integrator(integrator)
        r.set_initial_value(y0, t0).set_f_params(parameters)
        out = []
        while r.successful() and r.t <t1:
            r.integrate(r.t + dt)
            out.append(r.y)
        out = np.concatenate((t[:len(out)], np.array(out)), axis=1)
        out = pd.DataFrame(out, columns=col)
        return result_handle(out)

    fig = mplot(generate, t, **parameters)
    fig.add_subplot()
    fig.add_all()
    fig.show()


if __name__ == '__main__':
    def generate(x, a, phi):
        """
        generate sin and cos waves
        :param x: x scale
        :param a: amplitude
        :param phi: phase
        :return: pandas DataFrame with columns well defined
        """
        out = np.array([x, a * np.sin(x + phi), a * np.cos(x + phi)]).T
        return pd.DataFrame(out, columns=['x', 'sin', 'cos'])


    fig = mplot(generate, np.linspace(0, 10, 100), a=(1, 2), phi=(0, 2 * np.pi))
    # usage 1
    sub1 = fig.add_subplot(121)
    fig.add_line(sub1, 'x', 'sin', 'r', linewidth=2, label='sin')
    fig.add_line(sub1, 'x', 'cos', 'k-.', lw=4, label='cos')
    sub2 = fig.add_subplot(122)
    fig.add_line(sub2, 'sin', 'cos')
    fig.show()

    # usage 2
    # fig.add_subplot()
    # fig.add_all()
    # fig.show()
