<template>
    <div>
        <div v-show="loadError" class="errormsg"><strong>{{errorMsg}}</strong></div>
        <p>With this function it is possible to search for a person or a collection to discover the locations associated with him/her/it over the years.</p>
        <EntitySearcher ref="source" :classes="null" @query="query"/>
        <input type="submit" value="Search" id="button" @click="query"/>

        <AnalysisSearchResults v-show="showResults" :results="searchResults" @showEntity="showEntity"/>

        <AnalysisTable v-if="cursorID.length>0 && entitiesMap && actorLocationsTable" :entitiesMap="entitiesMap" :entityID="cursorID" :actorLocationsTable="actorLocationsTable" @displayTextOf="emitDisplayTextOf"/>
    </div>
</template>

<script>
import AnalysisTable from './AnalysisTable.vue';
import EntitySearcher from './EntitySearcher.vue'
import AnalysisSearchResults from './AnalysisSearchResults.vue'

export default {
    name: 'Analysis',
    props: {
        entitiesMap: Object,
        backend: String
    },

    components : {
        EntitySearcher,
        AnalysisTable,
        AnalysisSearchResults,
    },

    data() {
        return {
            loadError: false,
            errorMsg: "",


            actorLocationsTable: null,

            searchableEntities: [],
            maxSize: 40,
            showResults: false,
            searchResults: [],
            searchString: '',

            cursorID: ""
        }

    },

    methods: {
        fetchData() {
            fetch(this.backend + 'location_relations.json', {
                headers: {'Content-type': 'application/json', 'charset': 'utf-8'},
            }).then(res => res.ok && res.json()
            ).then(data => {
                if (data == undefined) {
                    this.errorMsg = "Couldn't fetch data from backend!";
                    this.loadError = true;
                } else {
                    this.loadError = false;
                    this.actorLocationsTable = data;
                    this.searchableEntities = Object.keys(this.actorLocationsTable);
                }
            });
        },

        emitDisplayTextOf(id) {
            this.$emit("displayTextOf", id);
        },

        query() {
            const sourceData = this.$refs.source.getData();
            const search_string = sourceData.searchString.replace(/[ -]/g, '').toLowerCase();
            if (search_string != this.searchString) {
                this.searchString = search_string;
                this.searchResults = Array.from(this.filterEntities());
            }
            this.showResults= true;
            
        },

        validEntity(entity) {
            return  entity.search_string.indexOf(this.searchString) != -1;
        },

        * filterEntities() {
            if (this.maxSize > this.searchableEntities.length) {
                this.maxSize = this.searchableEntities.length;
            }
            let count = 0;
            let cursor = null;
            /* BACKWARDS SEARCH:*/
            let i = this.searchableEntities.length-1;
            while (count < this.maxSize && i >= 0) {
                cursor = this.entitiesMap[this.searchableEntities[i]]
                if (this.validEntity(cursor)) { //(this.entities[i].search_string.indexOf(string) != -1 && this.entities[i].type.indexOf(this.sourceSearchClass) != -1)
                    yield cursor;
                    count++;
                }
                i--;
            }
        },

        showEntity(entityID) {
            this.cursorID = entityID;
            this.showResults = false;
        }

    },

    mounted()  {
        this.fetchData();
    },


}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
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
</style>
