<template>
    <div id="mask">
        <EntitySearcher class="gridItem" ref="source" :classes="entityClasses" @query="query"/>
        <PropertySearcher class="gridItem" ref="prop" :classes="propertyClasses" @query="query"/>
        <EntitySearcher class="gridItem" ref="target" :classes="entityClasses" @query="query"/>
    </div>
    <input type="submit" value="Search" id="button" @click="query"
    />
    
</template>

<script>
import EntitySearcher from './EntitySearcher.vue'
import PropertySearcher from './PropertySearcher.vue'
import SemanticClassStats from '../data/class_stats.json'

export default {
    name: 'QueryConstructor',
    components: {
        EntitySearcher,
        PropertySearcher
    },

    props: {
        entities: Array
    },

    data() {
        return {
            entityClasses: SemanticClassStats.Entities,
            propertyClasses: SemanticClassStats.Properties,
            searchResults: [],

            sourceSearchString: '',
            sourceSearchClass: '',
            propSearchClass: '',
            targetSearchString: '',
            targetSearchClass: '',

        }
    },

    emits: ['queryResults'],

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
            this.searchResults = Array.from(this.filterEntities());
            console.log(this.searchResults);
            this.$emit('queryResults', this.searchResults);
        },



        * filterEntities() {
            let maxSize = 20;
            if (maxSize > this.entities.length) {
                maxSize = this.entities.length;
            }
            let count = 0;
            /* BACKWARDS SEARCH:*/
            let i = this.entities.length-1;
            let string = this.sourceSearchString.toLowerCase();
            while (count < maxSize && i >= 0) {
                if (this.entities[i].lowered_text.indexOf(string) != -1 && this.entities[i].type.indexOf(this.sourceSearchClass) != -1) {
                    yield this.entities[i];
                    count++;
                }
                i--;
            }

            /* FOWARD SEARCH:
            let i = 0;
            let string = this.sourceSearchString.toLowerCase();
            while (count < maxSize && i < this.entities.length) {
                if (this.entities[i].lowered_text.indexOf(string) != -1 && this.entities[i].type.indexOf(this.sourceSearchClass) != -1) {
                    yield this.entities[i];
                    count++;
                }
                i++;
            }*/
        }
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
