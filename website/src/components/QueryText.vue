<template>
    <div>
        <QueryTextInfo/>
        <p>With this form it is possible to search the words annotated so far and/or filter the results by semantic class via the search options.</p>
        <EntitySearcher ref="source" :classes="stats.entityClasses" :possiblePredicates="possiblePredicates" @query="query"/>
        <input type="submit" value="Search" id="button" @click="query"/>

        <div v-show="loading" class="loadingMsg">
            <img class="loadingSymb" src="../assets/otter-solid.svg" alt="Loading Symbol"/>
            <p>Searching...</p>
        </div>

        <div id="navigationElements">
            <div v-if="historyCursor>0" class="navigationButton buttonLeft" @click="navigateHistory(-1)">🡸 Go Back</div>
            <div v-if="historyCursor<history.length-1" class="navigationButton buttonRight" @click="navigateHistory(1)" >Go Forward 🡺</div>
        </div>
        <TextSearchResults v-show="showResults" :results="searchResults" :texts="queryData.texts" @displayGraphOf="emitDisplayGraphOf" @showOneEntity="showOneEntity"/>
    </div>
</template>

<script>
import EntitySearcher from './EntitySearcher.vue'
import TextSearchResults from './TextSearchResults.vue'
import QueryTextInfo from './QueryTextInfo.vue'

export default {
    name: 'QueryText',
    components: {
        EntitySearcher,
        TextSearchResults,
        QueryTextInfo

    },
    props: {

        queryData : {
            properties: Array,
            entities:   Array,
            texts:      Object,
        },
        stats: {
            entityClasses:     Array,
            propertyClasses:   Array,
            parsedYears:       Array,
            parsedCollections: Array
        },
        showSingleEntity: Object
    },

    data() {
        return {
            showResults: false,
            loading: false,
            constrainedClasses: [],
            searchString: '',
            searchClass: '',
            searchResults: [],
            lastSingleEntity: null,
            possiblePredicates: null,
            
            history: [],
            historyCursor: -1,
            maxSize: 40

        }
    },

    watch: {
        showSingleEntity() {
            if (this.showSingleEntity != null) {
                this.lastSingleEntity = this.showSingleEntity;
                this.showOneEntity(this.lastSingleEntity);
            }
        }
    },

    methods: {
        getDataFromComponents() {
            const sourceData = this.$refs.source.getData();
            this.searchString = sourceData.searchString.replace(/[ -]/g, '').toLowerCase();
            this.searchClass = sourceData.searchClass;
            this.maxSize = sourceData.maxSize;
        },

        query() {
            this.loading = true;
            this.lastSingleEntity = null;
            this.getDataFromComponents();
            this.searchResults = Array.from(this.filterEntities());
            this.possiblePredicates = this.findPredicates();
            this.pushHistory();
            this.loading = false;
            this.showResults= true;
            
        },

        validEntity(entity) {
            return  entity.type.indexOf(this.searchClass) != -1
                    && entity.search_string.indexOf(this.searchString) != -1;
        },

        * filterEntities() {
            if (this.maxSize > this.queryData.entities.length) {
                this.maxSize = this.queryData.entities.length;
            }
            let count = 0;
            /* BACKWARDS SEARCH:*/
            let i = this.queryData.entities.length-1;
            while (count < this.maxSize && i >= 0) {
                if (this.validEntity(this.queryData.entities[i])) { //(this.entities[i].search_string.indexOf(string) != -1 && this.entities[i].type.indexOf(this.sourceSearchClass) != -1)
                    yield this.queryData.entities[i];
                    count++;
                }
                i--;
            }
        },

        findPredicates() {
            const foundProperties = [];

            for (let i = 0; i < this.searchResults.length; i++) {
                const element = this.searchResults[i];
                foundProperties.push(...element.outgoingProps);
                foundProperties.push(...element.incomingProps);
            }
            return new Set(foundProperties.map(p => p.type));

        },

        pushHistory() {
            if (this.searchResults.length > 0) {
                if (this.historyCursor != this.history.length-1) {
                    let delta = this.history.length-this.historyCursor-1;
                    this.history.splice(this.historyCursor+1, delta);
                }
                if (this.history.length > 15) this.history.shift();
                this.history.push(this.searchResults);
                this.historyCursor = this.history.length-1;
            }
        },

        navigateHistory(delta) {
            this.historyCursor = this.historyCursor + delta;
            if (0 <= this.historyCursor && this.historyCursor < this.history.length) {
                this.searchResults = this.history[this.historyCursor];
            } else {
                this.historyCursor =  this.historyCursor - delta;
            }
        },

        emitDisplayGraphOf(item_id) {
            this.$emit('displayGraphOf', item_id);
        },

        showOneEntity(entity) {
            this.searchResults = [entity];
            this.pushHistory();
            this.showResults = true;
        },

    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

    #navigationElements {
        display: block;
        width: 90%;
        margin-left: 5%;
    }

    .navigationButton {
        background: #FFFFFF;
        padding: 1ex;
        border: 1px solid #2c3e50;
        display: inline-block;

    }

    .navigationButton:hover {
        cursor: pointer;
        background: #EBEBEB;
    }

    .buttonRight {
        float: right;
    }

    .buttonLeft {
        float: left;
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

    .loadingMsg {
        text-align: center;
    }

    .loadingSymb {
        display: inline-block;
        width: 8em;
        height: 8em;

        animation-name:             loading;
        animation-duration:         3s;
        animation-iteration-count:  infinite;
    }

    @keyframes loading {
        0% {
            transform: rotate(0deg);
        }
        100% {
            transform: rotate(360deg);
        }
    }

    @media screen and (max-width: 700px) {
        .searchField {
            width: 100%;
            margin-left: 0%;
        }
    }
</style>
