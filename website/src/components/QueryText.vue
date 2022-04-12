<template>
    <div>
        <p>With this form it is possible to search the words annotated so far and/or filter the results by semantic class. Please note: the Results list is limited to {{maxSize}} entities in this prototype.</p>
        <EntitySearcher class="searchField" ref="source" :classes="constrainedClasses" @query="query"/>
        <input type="submit" value="Search" id="button" @click="query"/>

        <div id="navigationElements">
            <div v-if="historyCursor>0" class="navigationButton buttonLeft" @click="navigateHistory(-1)">🡸 Go Back</div>
            <div v-if="historyCursor<history.length-1" class="navigationButton buttonRight" @click="navigateHistory(1)" >Go Forward 🡺</div>
        </div>
        <TextSearchResults v-show="showResults" :results="searchResults" :texts="texts" @displayGraphOf="emitDisplayGraphOf" @showOneEntity="showOneEntity"/>
    </div>
</template>

<script>
import EntitySearcher from './EntitySearcher.vue'
import TextSearchResults from './TextSearchResults.vue'

export default {
    name: 'QueryText',
    components: {
        EntitySearcher,
        TextSearchResults

    },
    props: {
        properties: Array,
        entities: Array,
        texts: Object,
        stats: Object,
        showSingleEntity: Object
    },

    data() {
        return {
            showResults: false,
            constrainedClasses: [],
            searchString: '',
            searchClass: '',
            searchResults: [],
            lastSingleEntity: null,

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
            let sourceData = this.$refs.source.getData();
            this.searchString = sourceData.searchString.replace(/[ -]/g, '').toLowerCase();
            this.searchClass = sourceData.searchClass;
        },

        query() {
            this.lastSingleEntity = null;
            this.getDataFromComponents();
            this.searchResults = Array.from(this.filterEntities());
            this.pushHistory();
            this.showResults= true;
            
        },

        validEntity(entity) {
            return  entity.type.indexOf(this.searchClass) != -1
                    && entity.search_string.indexOf(this.searchString) != -1;
        },

        * filterEntities() {
            if (this.maxSize > this.entities.length) {
                this.maxSize = this.entities.length;
            }
            let count = 0;
            /* BACKWARDS SEARCH:*/
            let i = this.entities.length-1;
            while (count < this.maxSize && i >= 0) {
                if (this.validEntity(this.entities[i])) { //(this.entities[i].search_string.indexOf(string) != -1 && this.entities[i].type.indexOf(this.sourceSearchClass) != -1)
                    yield this.entities[i];
                    count++;
                }
                i--;
            }
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
        },

        navigateHistory(delta) {
            this.historyCursor = this.historyCursor + delta;
            if (0 <= this.historyCursor < this.history.length) {
                this.searchResults = this.history[this.historyCursor];
            } else {
                this.historyCursor =  this.historyCursor - delta;
            }
        },


        populateData() {
            //this.constrainedClasses = this.stats.entityClasses.filter(e => e.indexOf("E53") != -1 || e.indexOf("E21") != -1);
            this.constrainedClasses = this.stats.entityClasses;
        },

        emitDisplayGraphOf(item_id) {
            this.$emit('displayGraphOf', item_id);
        },

        showOneEntity(entity) {
            this.searchResults = [entity];
            this.pushHistory();
            this.showResults = true;
        },

    },

    mounted() {
        this.populateData();
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .searchField {
        text-align: center;
        width: 50%;
        margin-left: 25%;
    }

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
        width: 50%;
        background: #ffffff;
        margin-left: 25%;
        border: 1px solid #2c3e50;
    }
    
    #button:hover {
        background: #EBEBEB;
    }
</style>
