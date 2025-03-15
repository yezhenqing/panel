import numpy as np
import pandas as pd
import panel as pn
import pydeck as pdk
import param

pn.extension('deckgl', sizing_mode='stretch_width')


class DeckGLViewer(pn.viewable.Viewer):

    def __init__(self, **kwargs):
        super(DeckGLViewer, self).__init__(**kwargs)

        num_points, mean, std_dev = 5, 0, 10  # num_points 3 works, 5 doesn't work

        refx = np.random.normal(loc=mean, scale=std_dev, size=num_points)
        refy = np.random.normal(loc=mean, scale=std_dev, size=num_points)
        refz = np.ones(num_points) * 10
        
        self.ref_df = pd.DataFrame({
            'x': refx,    # <-line 22
            'position': np.vstack([refx, refy, refz]).T.tolist(),
            'fcolor': [[10., 180., 90.]] * num_points
        })
        
        qryx = np.random.normal(loc=mean, scale=std_dev, size=num_points)
        qryy = np.random.normal(loc=mean, scale=std_dev, size=num_points)
        qryz = np.ones(num_points) * 30

        self.qry_df = pd.DataFrame({
            'x': qryx,   #<-line 32
            'position': np.vstack([qryx, qryy, qryz]).T.tolist(),
            'fcolor': [(180., 18., 90.)] * num_points
        })
        

        self.ref_scatter_layer = self.create_scatterplot_layer(self.ref_df, id="ref_scatter_layer")
        self.qry_scatter_layer = self.create_scatterplot_layer(self.qry_df, id="qry_scatter_layer")

        self.layers = [
            self.ref_scatter_layer,
            self.qry_scatter_layer,
        ]

        self.render = self.create_deck_render()
    
        self.deckgl_pane = pn.pane.DeckGL(self.render, sizing_mode='stretch_both')
        self.param_pane = self.create_param_pane()

    def create_scatterplot_layer(self, data_df, id):
        scatter_layer = pdk.Layer(
            type="ScatterplotLayer",
            id=id,
            data=data_df,
            get_radius=2,
            get_position='position',
            pickable=True,
            get_fill_color='fcolor'
        )
        return scatter_layer

    def create_deck_render(self):
        INITIAL_VIEW_STATE = pdk.ViewState(
            target=[0, 0, 0],
            controller=True,
            rotation_x=-15,
            rotation_orbit=30,
            zoom=3,
            max_zoom=10,
            min_zoom=-2
        )

        orbit_view = pdk.View(
            type='OrbitView', 
            controller=True
        )

        render = pdk.Deck(
            api_keys={'mapbox': ""},
            layers=self.layers,
            initial_view_state=INITIAL_VIEW_STATE,
            map_style="light",
            map_provider=None,
            views=[orbit_view],
        )
        return render

    def create_param_pane(self):
        button = pn.widgets.Button(name='Click me', button_type='primary')
        button.on_click(self.test_click)
        param_box = pn.WidgetBox(
            pn.Column(
                button
            )
        )
        return param_box

    def test_click(self, event):
        print("Button clicked...")
        self.ref_df['fcolor'] = [[180, 18, 90]] * len(self.ref_df)
        self.qry_df['fcolor'] = [[10, 180, 90]] * len(self.qry_df)
        self.ref_scatter_layer.data = self.ref_df
        self.qry_scatter_layer.data = self.qry_df
        preTriggerObj = str(self.deckgl_pane.object)
        self.deckgl_pane.param.trigger('object')
        postTriggerObj = str(self.deckgl_pane.object)
        assert preTriggerObj == postTriggerObj

    def __panel__(self):
        return pn.Row(
            pn.Column(
              self.param_pane,
              width=300, 
              styles={'background':'lightgray'},
              sizing_mode='stretch_height'
            ),
            pn.Column(self.deckgl_pane)
        )

myviewer = DeckGLViewer()
myviewer.servable()