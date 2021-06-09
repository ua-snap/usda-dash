"""
Garden helper!
"""
# pylint: disable=invalid-name, import-error, line-too-long, too-many-arguments
from datetime import datetime
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html as ddsih
import luts
import dash_table
import geopandas as gpd


# Helper functions for GUI.
def wrap_in_section(content, section_classes="", container_classes="", div_classes=""):
    """
    Helper function to wrap sections.
    Accepts an array of children which will be assigned within
    this structure:
    <section class="section">
        <div class="container">
            <div>[children]...
    """
    return html.Section(
        className="section " + section_classes,
        children=[
            html.Div(
                className="container " + container_classes,
                children=[html.Div(className=div_classes, children=content)],
            )
        ],
    )


def wrap_in_field(label, control, className=""):
    """
    Returns the control wrapped
    in Bulma-friendly markup.
    """
    return html.Div(
        className="field " + className,
        children=[
            html.Label(label, className="label"),
            html.Div(className="control", children=control),
        ],
    )


header = ddsih.DangerouslySetInnerHTML(
    """
<div class="bannerstrip">University of Alaska Fairbanks&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;Alaska Climate Adaptation Science Center</div>
<header>
    <div class="container">
        <div class="titles">
            <h1 class="title is-1">Alaska Garden Helper</h1>
            <h2 class="subtitle is-2">How might growing conditions change in your part of Alaska in the coming decades?</h2>
        </div>
    </div>
</header>
<section class="introduction section">
    <div class="container content is-size-4">
    <p>Choose an Alaska community and see how its growing season has changed since 1980, and how it might change, out to 2099.</p>
	<p><em>Spoiler alert</em>: it may be getting longer!</p>

<p>You can also see graphs of daily minimum temperatures, growing degree days (and how this cumulative heat affects specific crops), and maps of projected hardiness (based on USDA Plant Hardiness Zones).</p>
        <p class="camera-icon">Click the <span>
            <svg viewBox="0 0 1000 1000" class="icon" height="1em" width="1em"><path d="m500 450c-83 0-150-67-150-150 0-83 67-150 150-150 83 0 150 67 150 150 0 83-67 150-150 150z m400 150h-120c-16 0-34 13-39 29l-31 93c-6 15-23 28-40 28h-340c-16 0-34-13-39-28l-31-94c-6-15-23-28-40-28h-120c-55 0-100-45-100-100v-450c0-55 45-100 100-100h800c55 0 100 45 100 100v450c0 55-45 100-100 100z m-400-550c-138 0-250 112-250 250 0 138 112 250 250 250 138 0 250-112 250-250 0-138-112-250-250-250z m365 380c-19 0-35 16-35 35 0 19 16 35 35 35 19 0 35-16 35-35 0-19-16-35-35-35z" transform="matrix(1 0 0 -1 0 850)"></path></svg>
        </span> icon in the upper-right of each chart to download it.</p>
    </div>
</section>
"""
)

### REUSED PIECES OF GUI ELEMENTS
threshold_picker = wrap_in_field(
    "Choose Minimum Temperature Threshold",
    dcc.Dropdown(
        id="threshold",
        options=[
            {"label": " 28°F (Hard Frost)", "value": 28},
            {"label": " 32°F (Light Frost)", "value": 32},
            {"label": " 40°F (Cold Crops)", "value": 40},
            {"label": " 50°F (Warm Crops)", "value": 50},
        ],
        value=32,
    ),
)


### START LENGTH OF GROWING SECTION

data_prefix = "https://s3-us-west-2.amazonaws.com/community-logs-data/"
season_table_data = gpd.read_file("season.csv")
communities = gpd.read_file("CommunityList.json")
names = list(communities.LocationName)

community_picker = wrap_in_field(
    "Choose community",
    dcc.Dropdown(
        id="community",
        options=[{"label": name, "value": name} for name in names],
        value="Fairbanks",
    ),
)

gcm_picker = wrap_in_field(
    "Choose Dataset",
    dcc.RadioItems(
        labelClassName="radio",
        options=[
            {"label": " Model Projection (GFDL)", "value": "GFDL"},
            {"label": " Model Projection (NCAR)", "value": "NCAR"},
        ],
        id="gcm",
        value="GFDL",
    ),
)

form_fields = wrap_in_section(
    html.Div(children=[community_picker, threshold_picker, gcm_picker])
)

logs_graph_layout = html.Div(className="container", children=[dcc.Graph(id="tcharts")])

data_table = dash_table.DataTable(
    id="season-table",
    columns=[
        {"name": "Baseline Temperature Threshold (°F)", "id": "baselinetemp"},
        {"name": "Species or Variety", "id": "species"},
        {"name": "Minimum number of days to maturity", "id": "mindaysmaturity"},
    ],
    style_cell={"whiteSpace": "normal", "textAlign": "left"},
    data=list(season_table_data.to_dict("index").values()),
)

logs_layout = wrap_in_section(
    html.Div(
        children=[
            html.H3("Length of Growing Season", className="title is-3"),
            logs_graph_layout,
            ddsih.DangerouslySetInnerHTML(
                f"""
                <div class="content narrative is-size-5">
                <h3 class="title is-3">Length of Growing Season</h3>
                <h4 class="title is-4">About growing season length</h4>
<p>
Longest recorded or projected stretch of time between the last cold day (based on the temperature threshold you select: 32°F, 40°F, or 50°F) and the first cold day thereafter. Here, you can see projections of start/end dates and the number of days in between. This can help you decide if a crop is worth planting in your area. ”Days to maturity” information is often provided on seed packets. But keep in mind that cool temperatures can slow growth, so also check our “Growing Degree Days” tool [BC -- revise this].</p>
<h4 class="title is-4">
How to choose a temperature threshold
</h4>
<p>Planting guides refer to “last frost” in spring and “first frost” in fall, implying minimum daily temperatures of 32°F. We offer more thresholds to provide flexibility in considering cold-hardy crops that may be harvested only when a hard frost is reached (28°F), or more delicate crops that cannot grow when temperatures are below a higher threshold. Such plants might be kept in a greenhouse until a later planting date, and harvested earlier.</p>
<h4 class="title is-4">
Why does the growing season seem so irregular?
</h4>
<p>
If you choose a high temperature threshold, or live in a very cold region, you may see results that look short and uneven, as you can see in this example showing days above 50F in Nome.
<img src="{luts.path_prefix}assets/nome.svg">
This is because the tool finds the longest consecutive period during which the daily minimum temperature never drops below the selected temperature. If just one day is below that value, the “season” ends at that point. Be sure to choose thresholds that make sense for your area.
</p>
<h4 class="title is-4">Sample Crops</h4>
                            """
            ),
            data_table,
        ]
    )
)

##### END LOGS

##### START ANNUAL MINIMUM TEMPS (amt)
amt_graph_layout = html.Div(className="container", children=[dcc.Graph(id="acharts")])

amt_layout = wrap_in_section(
    html.Div(
        children=[
            html.H3("Annual Minimum Temperatures", className="title is-3"),
            amt_graph_layout,
            dcc.Markdown(
                """
### Annual Minimum Temperature (AMT)
Perennials such as fruit trees and shrubs have to be hardy to survive Alaska winters. Many can’t withstand temperatures below certain thresholds.
##### Why we care about AMT
“Cold hardiness” is just one gauge of whether a crop is suitable to a particular region. Many other factors affect winter survival, such as the insulating value of snow, the moisture content of the ground, the presence or absence of permafrost, and the number of freeze-thaw cycles that occur. Future versions of this tool may include some of these factors.
##### How this tool calculates AMT
This graph shows modeled data based on the coldest temperature ever recorded or projected for a chosen location and time period. These temperatures are estimates of record-breaking cold. This differs from the data used for the zone maps, which are based on average coldest temperatures for 30-year periods. Zone maps will show slightly more moderate cold temperatures.
                        """,
                className="content narrative is-size-5",
            ),
        ]
    )
)
# END ANNUAL MINIMUM TEMPS

# START GROWING DEGREE DAYS

gdd_data_table = dash_table.DataTable(
    id="gdd-table",
    columns=[
        {"name": "Baseline Temperature Threshold (°F)", "id": "baselinetemp"},
        {"name": "Species or Variety", "id": "species"},
        {
            "name": "Minimum cumulative growing degree days to maturity",
            "id": "mindaysmaturity",
        },
    ],
    style_cell={"whiteSpace": "normal", "textAlign": "left"},
    data=list(gpd.read_file("gdd.csv").to_dict("index").values()),
)

gdd_graph_layout = html.Div(className="container", children=[dcc.Graph(id="ccharts")])

gdd_layout = wrap_in_section(
    html.Div(
        children=[
            html.H3("Growing Degree Days", className="title is-3"),
            gdd_graph_layout,
            dcc.Markdown(
                """
### Growing Degree Days (GDD)
Used to estimate how much heat is available to crops. Heat units are added up daily, throughout the growing season, to create a cumulative total. Plants tend to reach particular growth stages when cumulative GDD reaches the necessary values.
##### About temperature thresholds
Plants can grow when the temperature is above some minimum value, which varies by species. Many Alaska plants are cold-hardy and can grow on all above-freezing days. For these, GDD can be calculated with a baseline of 32°F. Most crops in other regions have higher baseline temperatures, such as 40°F for barley and oats, or 50°F for corn and tomatoes.
Choose a threshold based on what crop you plan to grow. For more information, click [here](#gdd-header)
##### How this tool measures GDD
We average daily high and low temperatures (based on our climate models) and subtracts the baseline value (which you choose) from that average.
Example: If you choose a baseline of 25°F, and if the daily high for a particular day was 72°F and the low was 45°F, the GDD value for that day would be (72°F + 45°F)/2 – 25°F = 33°F. Because heat stress is rare in Alaska, we did not include upper thresholds in our calculations.
##### What GDD means for you
GDD can help you plan what to plant—and what not to plant—especially when the length of the frost-free season does not provide enough information.
Example: Corn—with a baseline temperature of 50°F and over 2,000 GDD necessary for maturation—is unlikely to succeed in most parts of Alaska outside of a greenhouse, even though many varieties can mature in only 60-80 days, given enough heat.
&nbsp;""",
                className="content narrative is-size-5",
            ),
            gdd_data_table,
        ]
    )
)

# END GROWING DEGREE DAYS

# HARDINESS
hardiness_layout = wrap_in_section(
    ddsih.DangerouslySetInnerHTML(
        f"""
<h3 class="title is-3">Alaska Hardiness Maps</h3>
<div class="columns">
<div class="column">
<img src="{luts.path_prefix}assets/historical.png">
<img src="{luts.path_prefix}assets/10-39.png">
</div>
<div class="column">
<img src="{luts.path_prefix}assets/40-69.png">
<img src="{luts.path_prefix}assets/70-99.png">
</div>
</div>
</div>
<h4 class="title is-4">Download Maps</h4>
<p>
	<a href="https://www.sciencebase.gov/catalog/item/5be4a2fbe4b0b3fc5cf8bd4a">High Resolution Alaska Hardiness Maps</a>
</p>
<h4 class="title is-4">About Hardiness</h4>
<p>
The USDA uses Plant Hardiness Zones as the standard by which growers can determine which plants are likely to thrive at a given location. Many seed manufacturers reference these zones.  Hardiness maps are based on the average annual minimum winter temperature.  These zones are only a rough guide.  Because they are based on winter temperatures, they are of greatest importance for perennials such as fruit trees or peonies.  It may make more sense to choose summer crops (annuals) based on our Growing Degree Day or Growing Season tools. Also, variations based on very fine scale differences in slope or elevation are too small to show up on these maps.</p>
<h4 class="title is-4">Future Hardiness Projections</h4>
<p>These four maps represent current estimates of hardiness zones in Alaska, plus projections of how these zones may look in three future time periods, based on climate change models.  Looking at future zone maps can help guide long-term planting, and can also provide a starting point for discussions and further research about Alaska’s agricultural future.</p>
<p><a href="https://planthardiness.ars.usda.gov/PHZMWeb/">Find more information on USDA Hardiness Zones</a>.</p>
			"""
    ),
    div_classes="content narrative is-size-5",
)

current_year = datetime.now().year
footer = ddsih.DangerouslySetInnerHTML(
    f"""
<footer class="footer">
    <div class="container">
        <div class="columns">
            <div class="logos column is-one-fifth">
                <a href="https://www.gov.nt.ca/">
                    <img src="{luts.path_prefix}assets/AKCASC_color.svg" />
                </a>
                <br>
                <a href="https://uaf.edu/uaf/">
                    <img src="{luts.path_prefix}assets/UAF.svg" />
                </a>
            </div>
            <div class="column content is-size-5">
                <p>Created by the <a href="https://uaf-snap.org">Scenarios Network for Alaska + Arctic Planning</a>, a climate change research group at the International Arctic Research Center at the University of Alaska Fairbanks (UAF). Many Alaska farmers and gardeners provided input, including experts from the UAF Georgeson Botanical Gardens, Spinach Creek Farm, Calypso Farm, and the Alaska Peony Growers Association.
                </p>
            	<p>Developed in collaboration with the USDA Northwest Climate Hub with funding provided by the Alaska Climate Adaptation Science Center.
				</p>
                <p>Please contact <a href="mailto:uaf-snap-data-tools@alaska.edu">uaf-snap-data-tools@alaska.edu</a> if you have questions or would like to provide feedback for this tool. <a href="https://uaf-snap.org/tools-overview/">Visit the SNAP Climate + Weather Tools page</a> to see our full suite of interactive web tools.</p>
                <p>Copyright &copy; {current_year} University of Alaska Fairbanks.  All rights reserved.</p>
                <p>UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual.  <a href="https://www.alaska.edu/nondiscrimination/">Statement of Nondiscrimination</a> and <a href="https://www.alaska.edu/records/records/compliance/gdpr/ua-privacy-statement/">Privacy Statement</a>.</p>
            </div>
        </div>
    </div>
</footer>
"""
)

layout = html.Div(
    children=[
        header,
        form_fields,
        logs_layout,
        amt_layout,
        gdd_layout,
        hardiness_layout,
        footer
    ]
)
