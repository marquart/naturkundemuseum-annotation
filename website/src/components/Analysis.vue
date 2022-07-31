<template>
    <div>
        <div v-show="loadError" class="errormsg"><strong>{{errorMsg}}</strong></div>
        <p>As we annotated the acqusitions of objects over many years, it made sense to develop a tool which can be used to analyze the more consistent entities over the years more abstractly. It turned out that givers, original locations and the receiving collections are the most consistent information points. With the search bar below you can search for entities of either one of the three and get an overview of which of the entities of the other two types are connected to it over the years.</p>
        <p>The color and size indicate how much the author of the Chronik elaborated on each underlying acquisition compared to other acquisitions and can be interpreted as a level of appreciation of this specific transaction in the context of the gift economy. The more information the author packed into the description of a transaction, the higher the weight we gave it. The information points we have considered are primarily original locations (e.g. <span class="entityClick" @click="emitDisplayTextOf('11719')">"Dar-es-Salaam"</span>) & taxonomic classifications (e.g. <span class="entityClick" @click="emitDisplayTextOf('23459')">"Hirundo rustica"</span>) of the objects transferred and especially subjective assessments about the value and dimensions, like <span class="entityClick" @click="emitDisplayTextOf('44789')">"sauber präpariert"</span>, <span class="entityClick" @click="emitDisplayTextOf('34588')">"überaus wertvoll"</span> or <span class="entityClick" @click="emitDisplayTextOf('32397')">"sehr große Anzahl"</span>.</p>
        <p>The distribution of these weights over all identified acquisitions looks like this:</p>
        <AcquisitionsWeights/>
        <div class="modeselection">
            <p class="mode" :style="[mode === 0 ? focusStyle : unFocusStyle]" @click="navigate(0)">Givers</p>
            <p class="mode" :style="[mode === 1 ? focusStyle : unFocusStyle]" @click="navigate(1)">Locations</p>
            <p class="mode" :style="[mode === 2 ? focusStyle : unFocusStyle]" @click="navigate(2)">Collections</p>
        </div>
        <EntitySearcher ref="source" :classes="null" :possiblePredicates="null" @query="query"/>
        <input type="submit" value="Search" id="button" @click="query"/>

        <AnalysisSearchResults v-show="showResults" :results="searchResults" @showEntity="showEntity"/>

        <AnalysisTable v-if="entitiesMap && cursorResult != null && displayEntity != null" :entitiesMap="entitiesMap" :displayEntity="displayEntity" :entityData="cursorResult" @displayTextOf="emitDisplayTextOf"/>
    </div>
</template>

<script>
import AcquisitionsWeights from './SVG/AcquisitionsWeights.vue'
import AnalysisTable from './AnalysisTable.vue';
import EntitySearcher from './EntitySearcher.vue'
import AnalysisSearchResults from './AnalysisSearchResults.vue'

export default {
    name: 'Analysis',
    props: {
        inFocus: Boolean,
        entitiesMap: Object,
        backend: String
    },

    components : {
        AcquisitionsWeights,
        EntitySearcher,
        AnalysisTable,
        AnalysisSearchResults,
    },

    data() {
        return {
            focusStyle: {background: '#ffffff', color: "#7da30b"},
            unFocusStyle: {background: '#EBEBEB', },
            mode: 0,

            loadError: false,
            errorMsg: "",
            dataLoaded: false,

            personsLookup: null,
            locationsLookup: null,
            collectionsLookup: null,

            personTable: null,
            locationsTable: null,
            collectionsTable: null,

            maxSize: 40,
            showResults: false,
            searchResults: [],
            searchString: '',

            displayEntity: null,
            cursorResult: null
        }

    },

    watch: {
        async inFocus() {
            if (this.inFocus && !this.dataLoaded) {
                this.dataLoaded = await this.fetchData();
                if (this.dataLoaded) {
                    this.showEntity(this.personsLookup[0])
                }

            }
        }
    },

    methods: {
        async fetchData() {
            const rslt = await Promise.all([
                fetch(this.backend + 'Persons.json', {
                headers: {'Content-type': 'application/json', 'charset': 'utf-8'},
                }).then(res => res.ok && res.json() || Promise.reject(res)),
                fetch(this.backend + 'Locations.json', {
                headers: {'Content-type': 'application/json', 'charset': 'utf-8'},
                }).then(res => res.ok && res.json() || Promise.reject(res)),
                fetch(this.backend + 'Collections.json', {
                headers: {'Content-type': 'application/json', 'charset': 'utf-8'},
                }).then(res => res.ok && res.json() || Promise.reject(res))
            ]).then(data => {
                // handle data array here
                if (data == undefined || data.length != 3 || data[0] == undefined || data[1] == undefined || data[2] == undefined) {
                    this.errorMsg = "Couldn't fetch data from backend!";
                    this.loadError = true;
                    return false;
                } else {
                    this.loadError = false;
                    //Persons
                    this.personsLookup = data[0][0];
                    this.personTable   = data[0][1];
                    //Locations
                    this.locationsLookup = data[1][0];
                    this.locationsTable  = data[1][1];
                    //Collections
                    this.collectionsLookup = data[2][0];
                    this.collectionsTable  = data[2][1];
                    return true;
                }
            });
            return rslt
 
        },

        navigate(mode) {
            this.showResults = false;
            this.mode = mode;
            this.showEntity(this.personsLookup[0]);
        },

        emitDisplayTextOf(id) {
            this.$emit("displayTextOf", id);
        },

        async query() {
            if (!this.dataLoaded || this.personsLookup==null || this.locationsLookup==null ||this.collectionsLookup==null) this.dataLoaded = await this.fetchData();
            if (this.dataLoaded) {
                const sourceData = this.$refs.source.getData();
                const search_string = sourceData.searchString.replace(/[ -]/g, '').toLowerCase();
                this.searchResults = [];
                
                this.searchString = search_string;
                if (this.mode==0) this.filterEntities(this.personsLookup);
                else if (this.mode==1) this.filterEntities(this.locationsLookup);
                else if (this.mode==2) this.filterEntities(this.collectionsLookup);

                this.showResults= true;
            }
            
        },

        validEntity(entity) {
            return  entity.search_string.indexOf(this.searchString) != -1;
        },

        filterEntities(lookup) {
            if (this.maxSize > lookup.length) {
                this.maxSize = lookup.length;
            }
            let count = 0;
            let cursor = null
            /* BACKWARDS SEARCH:*/
            let i = lookup.length-1;
            while (count < this.maxSize && i >= 0) {
                /*cursor = this.entitiesMap[this.searchableEntities[i]]
                if (this.validEntity(cursor)) { //(this.entities[i].search_string.indexOf(string) != -1 && this.entities[i].type.indexOf(this.sourceSearchClass) != -1)*/
                cursor = lookup[i];
                if (cursor[0].indexOf(this.searchString) != -1) {
                    this.searchResults.push(cursor);
                    count++;
                }
                i--;
            }
        },

        showEntity(entity) {
            this.displayEntity = entity;
            if (this.mode==0)      this.cursorResult = this.personTable[entity[1]];
            else if (this.mode==1) this.cursorResult = this.locationsTable[entity[1]];
            else if (this.mode==2) this.cursorResult = this.collectionsTable[entity[1]];

            this.showResults = false;
        }

    },

    mounted()  {
        
    },


}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .modeselection {
        width: 80%;
        margin-left: 10%;
        display: grid;
        grid-template-columns: auto auto auto;
        align-content: center;
    }

    .mode {
        font-size: 1.2em;
        font-family: inherit;
        text-align: center;
        background: #ffffff;
        color: black;
        padding-top: 0.5em;
        padding-bottom: 0.5em;
        border-bottom: 5px solid #00000000;
    }

    .mode:hover {
        cursor: pointer;
        border-bottom: 5px solid #7da30b;
        color: #7da30b;
    }

    #button {
        box-sizing: border-box;
        display: inline;
        font-size: 1.2em;
        margin: 1.2em;
        font-family: inherit;
        color: inherit;
        cursor: pointer;
        text-align: center;
        width: 30%;
        background: #ffffff;
        margin-left: 35%;
        border: 1px solid #2c3e50;
    }
    
    #button:hover {
        background: #EBEBEB;
    }

    .entityClick {
        display: inline-block;
        padding: 1px;
        margin: 2px;
        border: 1px solid #f2f2f2;
        background: #FFF0;/*#EBEBEB;*/
        color: #7da30b;
        
    }

    .entityClick:hover {
        cursor: pointer;
        border: 1px solid #000000;
        text-decoration: underline;   
    }
</style>
