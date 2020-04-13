import pandas as pd
import bokeh.plotting as bo_po
import bokeh.palettes as bo_pa
import bokeh.layouts as bo_la
import bokeh.io as bo_io
import bokeh.models as bo_mo

def initialise_figure(y_axis_label):
    my_tools = 'pan,box_zoom,wheel_zoom,box_select,' + \
               'lasso_select,hover,reset,help'
    my_hover_tooltips = [("Datum", "@{Datum}"), ("Wert", "$y")]

    fig = bo_po.figure(x_axis_label='Datum',
                       y_axis_label=y_axis_label,
                       x_axis_type='datetime', tools=my_tools,
                       tooltips=my_hover_tooltips,
                       plot_width=700, plot_height=500,
                       # min_width=350, min_height=250,
                       # aspect_ratio=7./5.,
                       # sizing_mode='scale_both'
                       )
    return fig

def style_figure(fig, legend_loc):
    fig.xaxis.formatter = bo_mo.DatetimeTickFormatter(days="%d/%m/%y")
    fig.legend.location = legend_loc
    fig.legend.click_policy="hide"
    return fig

def plot_figure(yaxis_quantity, yaxis_label, legend_loc):
    bl_colors = {'Baden-Württemberg': bo_pa.Viridis10[2],
                 'Bayern': bo_pa.Viridis10[3],
                 'Berlin': bo_pa.Viridis10[4], 'Brandenburg': bo_pa.Viridis10[5],
                 'Bremen': bo_pa.Viridis10[6], 'Hamburg': bo_pa.Viridis10[7],
                 'Hessen': bo_pa.Viridis10[8],
                 'Mecklenburg-Vorpommern': bo_pa.Viridis10[9],
                 'Niedersachsen': bo_pa.Magma10[1],
                 'Nordrhein-Westfalen': bo_pa.Magma10[2],
                 'Rheinland-Pfalz': bo_pa.Magma10[3],
                 'Saarland': bo_pa.Magma10[4], 'Sachsen': bo_pa.Magma10[5],
                 'Sachsen-Anhalt': bo_pa.Magma10[6],
                 'Schleswig-Holstein': bo_pa.Magma10[7],
                 'Thüringen': bo_pa.Magma10[8]}
    fig = initialise_figure(yaxis_label)
    for land in bl_colors.keys():
        circ = fig.circle(x='Timestamp', y='{} {}'.format(land, yaxis_quantity),
                          source=my_source, legend_label='{}'.format(land),
                          color=bl_colors[land], size=13)
        if land != 'Baden-Württemberg':
            circ.visible = False
    fig = style_figure(fig, legend_loc)
    return fig

all_data = pd.read_csv('RKI_data/all_data.csv', index_col=0, parse_dates=[2])
my_source = bo_mo.ColumnDataSource(all_data)
bo_io.output_file("plot_rki_data.html")

figures_to_plot = {'fig1': ['Faelle pro 100000', 'Faelle pro 100000 Einwohner',
                            'top_left'],
                   'fig2': ['Todesfaelle pro 100000',
                            'Todesfaelle pro 100000 Einwohner', 'top_left'],
                   'fig3': ['Wachstumsrate (5d)', 'Wachstumsrate',
                            'top_right'],
                   'fig4': ['Verdopplungszeit (5d)', 'Verdopplungszeit in Tagen',
                            'top_left']
                   }
final_figure_list = []
for fig in figures_to_plot.keys():
    new_fig = plot_figure(figures_to_plot[fig][0], figures_to_plot[fig][1],
                          figures_to_plot[fig][2])
    final_figure_list.append(new_fig)

figure_grid = bo_la.gridplot(final_figure_list, ncols=1,
                             sizing_mode='scale_both')

bo_io.save(figure_grid)
bo_io.show(figure_grid)
