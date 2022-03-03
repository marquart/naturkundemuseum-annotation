<template>
    <div id="mask">
        <EntitySearcher class="gridItem" ref="source" @query="query"/>
        <PropertySearcher class="gridItem" ref="prop" @query="query"/>
        <EntitySearcher class="gridItem" ref="target" @query="query"/>
    </div>
    <input type="submit" value="Search" id="button" @click="query"
    />
    <SearchResults v-show="showResults" :results="searchResults"/>
</template>

<script>
import EntitySearcher from './EntitySearcher.vue'
import PropertySearcher from './PropertySearcher.vue'
import SearchResults from './SearchResults.vue'
import SemanticData from '../data/1906_Zoologische_172-215.json'

export default {
    name: 'QueryConstructor',
    components: {
        EntitySearcher,
        PropertySearcher,
        SearchResults
    },

    data() {
        return {
            showResults: false,
            entitiesMap: null,
            properties: [],
            entities: [],
            entitiesLength: 0,

            searchResults: [],

            sourceSearchString: '',
            sourceSearchClass: '',
            propSearchClass: '',
            targetSearchString: '',
            targetSearchClass: '',
        }
    },

    methods: {
        getDataFromComponents() {
            let sourceData = this.$refs.source.getData();
            //let propData = this.$refs.prop.getData();
            //let targetData = this.$refs.target.getData();

            this.sourceSearchString = sourceData.searchString;
            this.sourceSearchClass = sourceData.searchClass;
        },

        query() {
            this.getDataFromComponents();
            console.log(this.sourceSearchString);
            console.log(this.sourceSearchClass);
            this.showResults = true;
            this.searchResults = Array.from(this.filterEntities());
            console.log(this.searchResults);
        },

        loadData() {
            this.entitiesMap = SemanticData.Entities;
            this.properties = Object.values(SemanticData.Properties);
            this.properties.forEach(this.populateProperty);

            this.entities = Object.values(this.entitiesMap)
            this.entitiesLength = this.entities.length;
            console.log(this.entitiesLength);
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

        * filterEntities() {
            let maxSize = 20;
            if (maxSize > this.entitiesLength) {
                maxSize = this.entitiesLength;
            }
            let count = 0;
            let i = 0;
            let string = this.sourceSearchString.toLowerCase();
            while (count < maxSize && i < this.entitiesLength) {
                if (this.entities[i].text.toLowerCase().indexOf(string) != -1) {
                    yield this.entities[i];
                    count++;
                }
                i++;
            }
        },
    },

    mounted() {
        this.loadData();
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    #mask {
        display: grid;
        grid:
            'item item item';
        grid-auto-columns: minmax(0, 1fr);
        grid-auto-flow: column;
    }

    .gridItem {
        grid-area: 'item';
        display: block;
        text-align: center;
        margin: 5px;
        background: #ffffff;
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
