<template>
    <div id="app">
        <div id="heading">
            <img src="./assets/mfn-logo.png" alt="Naturkundemuseum Logo">
            <div id="heading-text">
                <h1>Provenance research under the spotlight</h1>
                <h2>Digital Edition of the Annual Reports of the Museum 1887–1915 and 1928–1938</h2>
            </div>
        </div>
        <div v-show="loadError" class="content errormsg"><strong>ERROR: {{errorMsg}}</strong></div>
        <div class="content" id="navigation">

            <div class="selectmode" :style="[mode === 0 ? focusStyle : unFocusStyle]"   @click="navigate(0)">Info</div>
            <div class="selectmode" :style="[mode === 1 ? focusStyle : unFocusStyle]"   @click="navigate(1)">Search</div>
            <!--<div class="selectmode" :style="[mode === 2 ? focusStyle : unFocusStyle]"   @click="navigate(2)">Query semantic Web</div>-->
            <div class="selectmode" :style="[mode === 3 ? focusStyle : unFocusStyle]"   @click="navigate(3)">Explore</div>

        </div>
        <div class="content">
            <Info  v-show="mode === 0"/>
            <QueryText v-show="mode === 1" :queryData="queryData" :stats="stats" :showSingleEntity="displayTextOfEntitity" @displayGraphOf="setDisplayGraphOf"/>
            <!--<Query v-show="mode === 2" :properties="properties" :entities="entities" :stats="stats" @displayGraphOf="setDisplayGraphOf"/>-->
            <Visualizations v-show="mode === 3" :entityId="displayGraphOfEntitity" :baseBackend="backend" @displayTextOf="setDisplayTextOf"/>
        </div>
    </div>
</template>

<script>
import Info from './components/Info.vue';
import QueryText from './components/QueryText.vue';
import Visualizations from './components/Visualizations.vue';


export default {
    name: 'App',
    components: {
        Info,
        QueryText,
        Visualizations
    },
    data() {
        let backend = "";
        if (process.env.NODE_ENV == "production") backend = "https://aron-marquart.de/mfn-chronik/assets/";
        else backend =  "./";
        return {
            focusStyle: {background: '#ffffff'},
            unFocusStyle: {background: '#EBEBEB'},
            mode: 0,
            displayGraphOfEntitity: "",
            displayTextOfEntitity: null,
            entitiesMap: {},

            queryData: {
                properties : [],
                entities: [],
                texts: {}, //text_id: array of lines
            },
            stats: {
                entityClasses:     [],
                propertyClasses:   [],
                parsedYears:       [],
                parsedCollections: []
            },
            
            backend: backend,
            loadError: false,
            errorMsg: "",
        }
    },

    methods: {
        navigate(mode) {
            this.mode = mode;
        },

        setDisplayGraphOf(item_id) {
            this.displayGraphOfEntitity = item_id;
            this.navigate(3);
        },

        setDisplayTextOf(item_id) {
            this.displayTextOfEntitity = this.entitiesMap[item_id];
            this.navigate(1);
        },

        fetchData() {
            Promise.all([
                fetch(this.backend + 'webdata.json', {
                headers: {'Content-type': 'application/json', 'charset': 'utf-8'},
                }).then(res => res.ok && res.json() || Promise.reject(res)),
                fetch(this.backend + 'class_stats.json', {
                headers: {'Content-type': 'application/json', 'charset': 'utf-8'},
                }).then(res => res.ok && res.json() || Promise.reject(res))
            ]).then(data => {
                // handle data array here
                if (data == undefined || data.length != 2 || data[0] == undefined || data[1] == undefined) {
                    this.errorMsg = "Couldn't fetch data from backend!";
                    this.loadError = true;
                } else {
                    this.loadError = false;
                    this.loadData(data);
                }
            });

        },

        loadData(data) {
            const SemanticData = data[0], SemanticClassStats = data[1];

            this.entitiesMap = SemanticData.Entities;
            let properties = Object.values(SemanticData.Properties);
            properties.forEach(this.populateProperty);

            const entities = Object.values(this.entitiesMap);
            const texts = SemanticData.Texts;
            console.log(entities.length);

            this.stats = {
                entityClasses: SemanticClassStats.Entities,
                propertyClasses:  SemanticClassStats.Properties,
                parsedYears:  SemanticClassStats.Years,
                parsedCollections:  SemanticClassStats.Institutions
            };

            this.queryData = {
                entities: entities,
                properties: properties,
                texts: texts
            };
        },

        populateProperty(element) {
            element.source = this.entitiesMap[element.source];
            element.target = this.entitiesMap[element.target];

            if (Object.prototype.hasOwnProperty.call(element.source, "outgoingProps")) {
                element.source.outgoingProps.push(element);
            } else {
                element.source.outgoingProps = [element];
            }

            if (Object.prototype.hasOwnProperty.call(element.target, "incomingProps")) {
                element.target.incomingProps.push(element);
            } else {
                element.target.incomingProps = [element];
            }

        },

    },
    mounted() {
        this.fetchData();
    },
}
</script>

<style>
    /*@import url('https://fonts.googleapis.com/css2?family=Open+Sans&display=swap');*/
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web&display=swap');

    body {
        /*background: linear-gradient(to bottom, #ffffff,  #f0f0f0);*/
        background: #f0f0f0;
        background-attachment: fixed;
        background-size: cover;
        margin: 0;
        height: 100%;
    }

    #app {
        font-family: "Titillium Web", "Open Sans", "Trade Gothic Next LT", Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        color: #2c3e50;
        margin-top: 20px;
    }

    .content {
        margin-left: 5%;
        margin-right: 5%;
        text-align: left;
        width: 90%;
        display: block;
        line-height: 1.5;
    }

    #navigation {
        border-bottom: 3px solid #7da30b;
        height: auto;
        display: grid;
        grid-template-columns: auto auto auto;
        align-content: center;

    }

    .selectmode {
        font-size: 1.2em;
        font-family: inherit;
        text-align: center;
        background: #ffffff;
        color: black;
        padding-top: 0.5em;
        padding-bottom: 0.5em;

    }

    .selectmode:hover {
        cursor: pointer;
      }

    img {

    }

    #heading {
        width: 90%;
        margin: 1%;
        display: grid;
        grid: 
          'logo headingText';
        align-items: center;
    }

    h1 {
        font-weight: bold;
        display: inherit;
    }

    h2 {
        font-weight: normal;
        display: inherit;
    }

    #heading-text {
        text-align: left;
        /*float: left;
        transform: translate(0, 100px);*/
        grid-area: 'headingText';
    }

    #heading img {
        height: 270px;
        grid-area: 'logo';
        /*position: relative;
        display: inline;
        float:left;
        margin-right: 10px;*/
    }

    .errormsg {
        font-size: 1.2em;
        font-family: inherit;
        text-align: center;
        background: red;
        color: white;
        border: 3px solid white;
        margin-bottom: 1ex;
    }

    @media screen and (max-width: 700px) {
        #heading  {
            grid: 
                'logo'
                'headingText';
        }

        #navigation {
            grid-template-columns: auto;
        }
    }
</style>
