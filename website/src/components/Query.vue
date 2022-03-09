<template>
    <div>
        <QueryConstructor :entities="entities" @queryResults="renderQueryResults"/>
        <div id="navigationElements">
            <div v-if="historyCursor>0" class="navigationButton buttonLeft" @click="navigateHistory(-1)">🡸 Go Back</div>
            <div v-if="historyCursor<history.length-1" class="navigationButton buttonRight" @click="navigateHistory(1)" >Go Forward 🡺</div>
        </div>
        <SearchResults v-show="showResults" :results="searchResults" @showOneEntity="showOneEntity" @displayGraphOf="emitDisplayGraphOf"/>
    </div>
</template>

<script>
import QueryConstructor from './QueryConstructor.vue'
import SearchResults from './SearchResults.vue'
import SemanticData from '../data/webdata.json'

export default {
    name: 'Query',
    components: {
        QueryConstructor,
        SearchResults
    },

    data() {
        return {
            showResults: false,

            entitiesMap: null,
            properties: [],
            entities: [],

            searchResults: [],
            history: [],
            historyCursor: -1

        }
    },

    emits: ['displayGraphOf'],

    mounted() {
        this.loadData();
    },

    methods: {
        showOneEntity(item) {
            this.searchResults = [item];
            this.pushHistory();
            this.showResults = true;

        },
        emitDisplayGraphOf(item_id) {
            this.$emit('displayGraphOf', item_id);
        },

        renderQueryResults(queryResult) {
            this.searchResults = queryResult;
            this.pushHistory();
            this.showResults = true;
        },

        pushHistory() {
            if (this.searchResults.length > 0) {
                if (this.historyCursor != this.history.length-1) {
                    let delta = this.history.length-this.historyCursor-1;
                    this.history.splice(this.historyCursor+1, delta);
                }
                if (this.history.length > 10) this.history.shift();
                this.history.push(this.searchResults);
                this.historyCursor = this.history.length-1;
            }
            //console.log(this.history.length);
        },

        navigateHistory(delta) {
            this.historyCursor = this.historyCursor + delta;
            if (0 <= this.historyCursor < this.history.length) {
                this.searchResults = this.history[this.historyCursor];
            } else {
                this.historyCursor =  this.historyCursor - delta;
            }
            console.log(this.historyCursor);
        },

        loadData() {
            this.entitiesMap = SemanticData.Entities;
            this.properties = Object.values(SemanticData.Properties);
            this.properties.forEach(this.populateProperty);

            this.entities = Object.values(this.entitiesMap)
            console.log(this.entities.length);
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
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    #navigationElements {
        display: block;
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
</style>
