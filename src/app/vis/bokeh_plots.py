import pandas as pd
from bokeh.models import GeoJSONDataSource, ColumnDataSource, CustomJS, Select, WMTSTileSource, Slider
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.tile_providers import STAMEN_TONER, STAMEN_TERRAIN
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Panel, Tabs, DataTable, DateFormatter, TableColumn, DateFormatter, HTMLTemplateFormatter

import numpy as np
import json


def plot_time_series(values, timestamps, 
                     plot_width=600, plot_height=400,
                     table_width=600, table_height=400):
    """ Returns Bokeh plot components for given property """

    timestamps = pd.to_datetime(timestamps).tolist()

    source = ColumnDataSource(data=dict(x=timestamps, y=values, times=[str(i) for i in timestamps]))

    p = figure(plot_width=plot_width, plot_height=plot_height, x_axis_type="datetime")

    p.line('x', 'y', source=source)


    columns = [
        TableColumn(field="times", width=100, title="Date, time"),
        TableColumn(field="y", width=100, title="Value")
        ]
    data_table = DataTable(source=source, columns=columns,
                           width=table_width, height=table_height)

    script, div = components({"plot": p, "table": data_table})


    return script, div

def plot_raster_series(raster, timestamps, 
                       resize_coef=None, plot_width=600, plot_height=400):
    """ Returns Bokeh plot components for given property """

    if resize_coef is not None:
        raster = raster.warp(
            {"width": int(raster.width * resize_coef),
             "height": int(raster.height * resize_coef),
             "scale": np.array(raster.scale)/resize_coef
            }
        )

    data = np.array(
        [np.flipud(i.data()) for i in raster.bands]
        )

    dw = [raster.width * raster.scale.x] * len(data)
    dh = [raster.height * raster.scale.y] * len(data)
    x0 = [raster.origin.x] * len(data)
    y0 = [raster.origin.y - raster.height * -1 * raster.scale.y] * len(data)


    hist, bins, width = [], [], []
    for i in data:
        hist_i, bins_i = np.histogram(i, bins='sturges')
        width_i = (bins_i[1]-bins_i[0])/2
        bins_i = (bins_i[1:] + bins_i[:-1]) / 2
        hist.append(hist_i)
        bins.append(bins_i)
        width.append(width_i)

    hist, bins, width = np.array(hist), np.array(bins), np.array(width)

    source = ColumnDataSource(data=dict(
        x=x0, y=y0, dw=dw, dh=dh, img=data, hist=hist, bins=bins, width=width,
        x_init=x0[:1], y_init=y0[:1], dw_init=dw[:1], dh_init=dh[:1], img_init=data[:1],
        hist_init=hist[0], bins_init=bins[0]))


    raster = figure(plot_width=plot_width, plot_height=plot_height,
                    x_range=[x0[0], x0[0] + dw[0]], y_range=[y0[0], y0[0] + dh[0]])

    raster.image(image='img_init', x='x', y='y', dw='dw', dh='dh',
                 palette="Spectral11", source=source)
    raster.add_tile(STAMEN_TONER)

    print(x0[0], x0[0] + dw[0], y0[0], y0[0] + dh[0])

    histogram = figure(
        x_range=[data.min(), data.max()],
        y_range=[0, len(data[0].flatten())],
        width=300, height=300
        )
    histogram.vbar(x='bins_init', top='hist_init', width=width.mean(), source=source)

    callback = CustomJS(args=dict(source=source), code="""
            var data = source.data;
            var idx = cb_obj.value;
            console.log(data['hist_init'], data['bins_init'], data['width_init']);
            data['img_init'] = [data['img'][idx]];
            data['hist_init'] = data['hist'][idx];
            data['bins_init'] = data['bins'][idx];
            data['width_init'] = data['width'][idx];
            source.trigger('change');
            console.log(data['hist_init'], data['bins_init'], data['width_init']);
        """)
    slider = Slider(
        start=0, end=len(data), value=0, step=1,
        title='Select time step',
        callback=callback
        )
    controls = widgetbox(slider, width=200)

    script, div = components({"raster_map": raster, "plot": histogram, "controls": controls})


    return script, div

def plot_single_raster(raster, resize_coef=1., plot_width=600, plot_height=400,
                       table_width=600, table_height=400):
    """ Returns Bokeh plot components for given property """

    raster = raster.value

    if resize_coef is not None:
        # raster = raster.warp(
        #     {"width": int(raster.width * resize_coef),
        #      "height": int(raster.height * resize_coef),
        #      "scale": np.array(raster.scale)/resize_coef
        #     }
        # )
        raster = raster.warp(
            {"width": int(raster.width * resize_coef),
             "height": int(raster.height * resize_coef),
             "scale": np.array(raster.scale)/resize_coef
            }
        )

    data = np.array(
        [np.flipud(i.data()) for i in raster.bands]
        )

    dw = [raster.width * raster.scale.x] * len(data)
    dh = [raster.height * raster.scale.y] * len(data)
    x0 = [raster.origin.x] * len(data)
    y0 = [raster.origin.y - raster.height * -1 * raster.scale.y] * len(data)


    hist, bins, width = [], [], []
    for i in data:
        hist_i, bins_i = np.histogram(i, bins='sturges')
        width_i = (bins_i[1]-bins_i[0])/2
        bins_i = (bins_i[1:] + bins_i[:-1]) / 2
        hist.append(hist_i)
        bins.append(bins_i)
        width.append(width_i)

    hist, bins, width = np.array(hist), np.array(bins), np.array(width)

    source = ColumnDataSource(data=dict(
        x_init=x0[:1], y_init=y0[:1], dw_init=dw[:1], dh_init=dh[:1], img_init=data[:1],
        hist_init=hist[0], bins_init=bins[0]
        )
    )

    raster = figure(plot_width=plot_width, plot_height=plot_height,
                    x_range=[x0[0], x0[0] + dw[0]], y_range=[y0[0], y0[0] + dh[0]])
    raster.image(image='img_init', x='x_init', y='y_init', dw='dw_init', dh='dh_init',
                 palette="Spectral11", source=source)
    raster.add_tile(STAMEN_TONER)

    histogram = figure(
        x_range=[data.min(), data.max()],
        y_range=[0, len(data[0].flatten())],
        width=300, height=300
        )
    histogram.vbar(x='bins_init', top='hist_init', width=width.mean(), source=source)

    script, div = components({"raster_map": raster, "plot": histogram})

    return script, div
