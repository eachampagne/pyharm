# Various full figures, combining plots & settings frequently used together
# Similar to reports.py in imtools

import os
import sys
from turtle import filling
import psutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

# 
from ..reductions import *
from ..variables import *
from .plot_dumps import *
from .plot_results import *
from ..defs import FloorFlag_KHARMA, FloorFlag_iharm3d, InversionStatus

"""Various full figures, combining plots & settings frequently used together
Similar to reports.py in imtools
"""

def simplest(fig, dump, diag, plotrc, type="both", var='log_rho'):
    """Simplest movie: show log-variable without color bars for outreach animations
    Note this figure uses different colorbars for left & right plots!
    Also note that if you really want just poloidal/toroidal, you likely want to play with aspect ratio
    """
    if type == "both":
        xz_slc = plt.subplot(1, 2, 1)
        xy_slc = plt.subplot(1, 2, 2)
    else:
        xz_slc = plt.subplot(1, 1, 1)
        xy_slc = plt.subplot(1, 1, 1)
    
    if 'vmin' not in plotrc or plotrc['vmin'] is None:
        plotrc['vmin'] = -6
    if 'vmax' not in plotrc or plotrc['vmax'] is None:
        plotrc['vmax'] = 1

    if type in ("poloidal", "both"):
        plot_xz(xz_slc, dump, var, label="",
                xlabel=False, ylabel=False, xticks=[], yticks=[],
                cbar=False, frame=False, **plotrc)
    if type in ("toroidal", "both"):
        plotrc['vmin'] = plotrc['vmin'] + 0.15
        plotrc['vmax'] = plotrc['vmax'] + 0.15
        plot_xy(xy_slc, dump, var, label="",
                xlabel=False, ylabel=False, xticks=[], yticks=[],
                cbar=False, frame=False, **plotrc)
    xz_slc.axis('off')
    xy_slc.axis('off')
    fig.subplots_adjust(hspace=0, wspace=0, left=0, right=1, bottom=0, top=1)
    return fig


def simpler(fig, dump, diag, plotrc):
    """Simpler movie: rho and EH magnetization"""
    gs = gridspec.GridSpec(2, 2, height_ratios=[6, 1], width_ratios=[16, 17])
    ax_slc = [plt.subplot(gs[0, 0]), plt.subplot(gs[0, 1])]
    ax_flux = [plt.subplot(gs[1, :])]
    plot_slices(ax_slc[0], ax_slc[1], dump, 'rho', log=True, **plotrc)
    plot_hst(ax_flux[0], diag, 'phi_b', tline=dump['t'])
    return fig

def simple(fig, dump, diag, plotrc):
    """Simple movie: RHO mdot phi"""
    gs = gridspec.GridSpec(3, 2, height_ratios=[4, 1, 1])
    ax_slc = [plt.subplot(gs[0, 0]), plt.subplot(gs[0, 1])]
    ax_flux = [plt.subplot(gs[1, :]), plt.subplot(gs[2, :])]
    plot_slices(ax_slc[0], ax_slc[1], dump, 'rho', log=True, **plotrc)
    plot_hst(ax_flux[0], diag, 'Mdot', tline=dump['t'], xlabel="", xticklabels=[])
    plot_hst(ax_flux[1], diag, 'phi_b', tline=dump['t'])
    fig.subplots_adjust(hspace=0.25, bottom=0.05, top=0.95)
    return fig

def traditional(fig, dump, diag, plotrc):
    """8-pane movie: XZ and XY slices of rho & UU on top, bsq and beta on the bottom.
    Alternatively, mix in zoomed-in versions or fluxed from the dignostic output
    """
    ax_slc = lambda i: plt.subplot(2, 4, i)
    ax_flux = lambda i: plt.subplot(4, 2, i)
    # Usual movie: RHO beta fluxes
    # CUTS
    plot_slices(ax_slc(1), ax_slc(2), dump, 'rho', log=True, **plotrc)
    plot_slices(ax_slc(3), ax_slc(4), dump, 'UU', log=True, **{**plotrc, **{'ylabel': False}})
    plot_slices(ax_slc(5), ax_slc(6), dump, 'beta', log=True, **plotrc)
    # FLUXES
    plot_hst(ax_flux(6), diag, 'Mdot', tline=dump['t'], xticklabels=[])
    plot_hst(ax_flux(8), diag, 'phi_b', tline=dump['t'])
    # bsq
    #plot_slices(ax_slc(7), ax_slc(8), dump, 'bsq', log=True, **plotrc)
    # Zoomed in rho
    #plot_slices(ax_slc(7), ax_slc(8), dump, 'rho', log=True, window=[-10, 10, -10, 10])
    fig.subplots_adjust(hspace=0.1, wspace=0.23, left=0.05, right=0.95, bottom=0.05, top=0.95)
    return fig

def prims(fig, dump, diag, plotrc, log=True, simple=True, type="poloidal"):
    ax_slc = lambda i: plt.subplot(2, 4, i)
    if type == "poloidal":
        fn = plot_xz
    else:
        fn = plot_xy
    if simple:
        plotrc.update({'xlabel': False, 'ylabel': False,
                       'xticks': [], 'yticks': [],
                       'cbar': False, 'frame': False})
    for i,var in enumerate(['RHO', 'UU', 'U1', 'U2', 'U3', 'B1', 'B2', 'B3']):
        fn(ax_slc(i+1), dump, var, log=log, **plotrc)
    if simple:
        fig.subplots_adjust(hspace=0, wspace=0, left=0, right=1, bottom=0, top=0.95)
    return fig

def vecs_prim(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(2, 4, i)
    # Usual movie: RHO beta fluxes
    # CUTS
    plot_slices(ax_slc(1), ax_slc(5), dump, 'rho', log=True, average=True, **plotrc)

    for i,var in zip((2,3,4,6,7,8), ("U1", "U2", "U3", "B1", "B2", "B3")):
        plot_xz(ax_slc(i), dump, var, log=True, **plotrc)
    
    return fig

def vecs_cov(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(2, 4, i)
    for i,var in zip((1,2,3,4,5,6,7,8), ("u_0", "u_r", "u_th", "u_3","b_0", "b_r", "b_th", "b_3")):
        plot_xz(ax_slc(i), dump, var, log=True, **plotrc)
    
    return fig

def vecs_con(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(2, 4, i)
    for i,var in zip((1,2,3,4,5,6,7,8), ("u^0", "u^r", "u^th", "u^3","b^0", "b^r", "b^th", "b^3")):
        plot_xz(ax_slc(i), dump, var, log=True, **plotrc)
    
    return fig

def ejection(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(1, 2, i)
    # Usual movie: RHO beta fluxes
    # CUTS
    plot_xz(ax_slc(1), dump, 'rho', label=pretty('rho')+" phi-average", average=True, **plotrc)
    plot_xz(ax_slc(2), dump, 'bsq', label=pretty('bsq')+" phi-average", average=True, **plotrc)
    return fig

def b_bug(fig, dump, diag, plotrc):
    rmax = 10
    thmax = 10
    phi = 100
    ax_slc = lambda i: plt.subplot(1, 3, i)
    ax_slc(1).pcolormesh(dump['X1'][:rmax,0:thmax,phi], dump['X2'][:rmax,0:thmax,phi], dump['b^r'][:rmax,0:thmax,phi], vmax=0, vmin=-4)
    ax_slc(2).pcolormesh(dump['X1'][:rmax,0:thmax,phi], dump['X2'][:rmax,0:thmax,phi], dump['b^th'][:rmax,0:thmax,phi], vmax=0, vmin=-4)
    ax_slc(3).pcolormesh(dump['X1'][:rmax,0:thmax,phi], dump['X2'][:rmax,0:thmax,phi], dump['b^3'][:rmax,0:thmax,phi], vmax=0, vmin=-4)
    return fig

def e_ratio(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(2, 4, i)
    plotrc['vmin'] = -3
    plotrc['vmax'] = 3
    # Energy ratios: difficult places to integrate, with failures
    plot_slices(ax_slc(1), ax_slc(2), dump, np.log10(dump['UU'] / dump['RHO']),
                        label=r"$\log_{10}(U / \rho)$", average=True, **plotrc)
    plot_slices(ax_slc(3), ax_slc(4), dump, np.log10(dump['bsq'] / dump['RHO']),
                        label=r"$\log_{10}(b^2 / \rho)$", average=True, **plotrc)
    plot_slices(ax_slc(5), ax_slc(6), dump, np.log10(1 / dump['beta']),
                        label=r"$\beta^{-1}$", average=True, **plotrc)
    plotrc['vmin'] = 0
    plotrc['vmax'] = 20
    plotrc['cmap'] = 'Reds'
    plot_slices(ax_slc(7), ax_slc(8), dump, (dump['pflag'] > 0).astype(np.int32),
                        label="Failures", sum=True, **plotrc)
    return fig

def e_ratio_funnel(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(1, 4, i)
    # Energy ratios: difficult places to integrate, with failures

    r1d = dump['r'][:,0,0]
    r_i = i_of(r1d, plotrc['radius'])
    plotrc['vmin'] = -3
    plotrc['vmax'] = 3
    plotrc['half_cut'] = True
    plot_thphi(ax_slc(1), dump, 'log_Theta', r_i,
                        label=r"$\log_{10}(U / \rho)$", average=True, **plotrc)
    plot_thphi(ax_slc(2), dump, 'log_sigma', r_i,
                        label=r"$\log_{10}(b^2 / \rho)$", average=True, **plotrc)
    plot_thphi(ax_slc(3), dump, 'log_betainv', r_i,
                        label=r"$\beta^{-1}$", average=True, **plotrc)
    plotrc['vmin'] = 0
    plotrc['vmax'] = 20
    plotrc['cmap'] = 'Reds'
    plot_thphi(ax_slc(4), dump, (dump['pflag'] > 0).astype(np.int32), r_i,
                        label="Failures", sum=True, **plotrc)
    return fig

def conservation(fig, dump, diag, plotrc):
    """TODO this is still WIP to restore. Later."""
    ax_slc = lambda i: plt.subplot(2, 4, i)
    ax_flux = lambda i: plt.subplot(4, 2, i)
    # Continuity plots to verify local conservation of energy, angular + linear momentum
    # Integrated T01: continuity for momentum conservation
    plotrc['native'] = True
    plotrc['vmin'] = 0
    plotrc['vmax'] = 2000
    plot_slices(ax_slc(1), ax_slc(2), dump, 'JE1', label=r"$T^1_0$ Integrated", sum=True)

    # integrated T00: continuity plot for energy conservation
    plotrc['vmax'] = 3000
    plot_slices(ax_slc(5), ax_slc(6), dump, 'JE0', label=r"$T^0_0$ Integrated", sum=True)

    # Usual fluxes for reference
    #ppltr.plot_hst(ax_flux[1], diag, 'Mdot', tline=dump['t'], logy=MDOT)

    r_out = 100

    # Radial conservation plots
    E_r = shell_sum(dump, T_mixed(dump, 0, 0))
    Ang_r = shell_sum(dump, T_mixed(dump, 0, 3))
    mass_r = shell_sum(dump, dump['ucon'][0] * dump['RHO'])
    r1d = dump['r'][:,0,0]

    max_e = 50000
    # TODO these will need some work to fully go to just ax.plot calls
    ax_flux(2).plot(r1d, np.abs(E_r), title='Conserved vars at R', ylim=(0, max_e), rlim=(0, r_out), label="E_r")
    ax_flux(2).plot(r1d, np.abs(Ang_r) / 10, ylim=(0, max_e), rlim=(0, r_out), color='r', label="L_r")
    ax_flux(2).plot(r1d, np.abs(mass_r), ylim=(0, max_e), rlim=(0, r_out), color='b', label="M_r")
    ax_flux(2).legend()

    # Radial energy accretion rate
    Edot_r = shell_sum(dump, T_mixed(dump, 1, 0))
    ax_flux(4).plot(r1d, Edot_r, label='Edot at R', ylim=(-200, 200), rlim=(0, r_out), native=True)

    # Radial integrated failures
    ax_flux(6).plot(r1d, (dump['pflag'] > 0).sum(axis=(1, 2)), label='Fails at R', native=True, rlim=(0, r_out), ylim=(0, 1000))

    return fig

def energies(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(2, 4, i)
    # Set particular vmin/max
    plotrc['half_cut'] = True
    plotrc['vmin'] = -3
    plotrc['vmax'] = 3
    # Energy ratios: difficult places to integrate, with failures
    plot_slices(ax_slc(1), ax_slc(2), dump, 'rho',
                label=r"$\log_{10}(\rho)$", average=True, **plotrc)
    plot_slices(ax_slc(3), ax_slc(4), dump, 'bsq',
                label=r"$\log_{10}(b^2)$", average=True, **plotrc)
    plot_slices(ax_slc(5), ax_slc(6), dump, 'UU',
                label=r"$\log_{10}(UU)$", average=True, **plotrc)
    plotrc['vmin'] = 0
    plotrc['vmax'] = 20
    plotrc['cmap'] = 'Reds'
    plot_slices(ax_slc(7), ax_slc(8), dump, (dump['pflag'] > 0).astype(np.int32),
                        label="Failures", sum=True, **plotrc)

    return fig

def floors(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(2, 5, i)
    plotrc['xlabel'] = False
    plotrc['xticks'] = []
    plot_xz(ax_slc(1), dump, 'rho', log=True, **plotrc)
    plotrc['vmin'] = 0
    plotrc['vmax'] = 20
    plotrc['cmap'] = 'Reds'
    for i,ff in enumerate(FloorFlag_KHARMA):
        p = 2+i
        plotrc['cbar'] = (p % 5 == 0)
        if p <= 5:
            plotrc['xlabel'] = False
            plotrc['xticks'] = []
        else:
            plotrc['xlabel'] = True
            plotrc['xticks'] = None

        if p % 5 != 1:
            plotrc['ylabel'] = False
            plotrc['yticks'] = []
        else:
            plotrc['ylabel'] = True
            plotrc['yticks'] = None

        plot_xz(ax_slc(p), dump, dump['fflag'] & ff.value, label=ff.name, sum=True, **plotrc)
    fig.subplots_adjust(hspace=0.1, wspace=0.12, left=0.05, right=0.95, bottom=0.05, top=0.92)
    fig.suptitle("t = {}, Total floor hits: {}".format(int(dump['t']), np.sum(dump['fflag'] > 0)))
    return fig

def fails(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(2, 4, i)
    plotrc['xlabel'] = False
    plotrc['xticks'] = []
    plot_xz(ax_slc(1), dump, 'rho', log=True, **plotrc)
    plotrc['vmin'] = 0
    plotrc['vmax'] = 1
    plotrc['cmap'] = 'Reds'
    for i in range(1, 8):
        p = 1+i
        plotrc['cbar'] = (p % 4 == 0)
        if p <= 4:
            plotrc['xlabel'] = False
            plotrc['xticks'] = []
        else:
            plotrc['xlabel'] = True
            plotrc['xticks'] = None

        if p % 4 != 1:
            plotrc['ylabel'] = False
            plotrc['yticks'] = []
        else:
            plotrc['ylabel'] = True
            plotrc['yticks'] = None

        plot_xz(ax_slc(p), dump, dump['pflag'] == i, label=InversionStatus(i).name, sum=True, **plotrc)
    fig.subplots_adjust(hspace=0.1, wspace=0.12, left=0.05, right=0.95, bottom=0.05, top=0.92)
    fig.suptitle("t = {}, Total inversion failures: {}".format(int(dump['t']), np.sum(dump['pflag'] > 0)))
    return fig

def old_floors(fig, dump, diag, plotrc):
    ax_slc = lambda i: plt.subplot(2, 3, i)
    plot_xz(ax_slc(1), dump, 'rho', label=pretty('rho'), **plotrc)
    plotrc['vmin'] = 0
    plotrc['vmax'] = 20
    plotrc['cmap'] = 'Reds'
    for i,ff in enumerate(FloorFlag_iharm3d):
        plot_xz(ax_slc(2+i), dump, dump['fflag'] & ff.value, label=ff.name, sum=True, **plotrc)

    return fig