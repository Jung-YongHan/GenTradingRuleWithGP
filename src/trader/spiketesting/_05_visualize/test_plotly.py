# Data Visualization
from plotly.subplots import make_subplots
import plotly.graph_objects as go

epoch_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
loss_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
val_loss_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
error_rate = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
val_error_rate = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

loss_plots = [go.Scatter(x=epoch_list,
                         y=loss_list,
                         mode='lines',
                         name='Loss',
                         line=dict(width=4)),
              go.Scatter(x=epoch_list,
                         y=val_loss_list,
                         mode='lines',
                         name='Validation Loss',
                         line=dict(width=4))]

loss_figure = go.Figure(data=loss_plots)

error_plots = [go.Scatter(x=epoch_list,
                          y=loss_list,
                          mode='lines',
                          name='Error Rate',
                          line=dict(width=4)),
               go.Scatter(x=epoch_list,
                          y=val_loss_list,
                          mode='lines',
                          name='Validation Error Rate',
                          line=dict(width=4))]

error_figure = go.Figure(data=error_plots)

metric_figure = make_subplots(
    rows=3, cols=2,
    specs=[[{}, {}],
           [{}, {}],
           [{'colspan': 2}, {}]])

for t in loss_figure.data:
    metric_figure.append_trace(t, row=1, col=1)
for t in error_figure.data:
    metric_figure.append_trace(t, row=1, col=2)
metric_figure.show()