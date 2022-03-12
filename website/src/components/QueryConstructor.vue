<template>
    <YearSearcher ref="report" :years="stats.parsedYears" :collections="stats.parsedCollections"/>
    <div id="mask">
        <EntitySearcher class="gridItem" ref="source" :classes="stats.entityClasses" @query="query"/>
        <PropertySearcher class="gridItem" ref="prop" :classes="stats.propertyClasses" @query="query"/>
        <EntitySearcher class="gridItem" ref="target" :classes="stats.entityClasses" @query="query"/>
    </div>
    <input type="submit" value="Search" id="button" @click="query"
    />
    
</template>

<script>
import YearSearcher from './YearSearcher.vue'
import EntitySearcher from './EntitySearcher.vue'
import PropertySearcher from './PropertySearcher.vue'


export default {
    name: 'QueryConstructor',
    components: {
        EntitySearcher,
        PropertySearcher,
        YearSearcher
    },

    props: {
        entities: Array,
        stats: Object
    },

    data() {
        return {
            /*entityClasses: stats.entityClasses,
            propertyClasses: stats.propertyClasses,
            parsedYears: stats.parsedYears,
            parsedCollections: stats.parsedCollections,*/
            searchResults: [],

            sourceSearchYear: 0,
            sourceSearchCollection: '',
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
            let reportData = this.$refs.report.getData();

            this.sourceSearchYear = reportData.searchYear;
            this.sourceSearchCollection = reportData.searchCollection;
            this.sourceSearchString = sourceData.searchString.toLowerCase();
            this.sourceSearchClass = sourceData.searchClass;
        },

        query() {
            this.getDataFromComponents();
            this.searchResults = Array.from(this.filterEntities());
            this.$emit('queryResults', this.searchResults);
        },

        validEntity(entity) {
            let tmpYear = 0;
            if (this.sourceSearchYear>0) tmpYear = this.sourceSearchYear;
            else tmpYear = entity.year;

            return  entity.year === tmpYear
                    && entity.institution.indexOf(this.sourceSearchCollection) != -1
                    && entity.type.indexOf(this.sourceSearchClass) != -1
                    && entity.lowered_text.indexOf(this.sourceSearchString) != -1;
        },

        * filterEntities() {
            let maxSize = 40;
            if (maxSize > this.entities.length) {
                maxSize = this.entities.length;
            }
            let count = 0;
            /* BACKWARDS SEARCH:*/
            let i = this.entities.length-1;
            while (count < maxSize && i >= 0) {
                if (this.validEntity(this.entities[i])) { //(this.entities[i].lowered_text.indexOf(string) != -1 && this.entities[i].type.indexOf(this.sourceSearchClass) != -1)
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
        align-self: stretch;
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
