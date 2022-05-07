<template>
    <div class="analyzeResults">
        <h3>Search results:</h3>
        <p
            v-for="entity in results"
            :key="entity.id"
            class="analyzeResultsItem"
            @click="emitID(entity.id)"

        >
        {{entity.text}}
        </p>
    </div>
</template>

<script>


export default {
    name: 'Analysis',
    props: {
        results: Array
    },

    components : {

    },

    data() {
        return {

        }

    },

    methods: {
        emitID(entityID) {
            this.$emit("showEntity", entityID);
        }


    },

    mounted()  {

    },


}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .analyzeResults {
        text-align: center;
        width: 50%;
        margin-left: 25%;
    }

    .analyzeResultsItem {
        padding: 4px;
        margin: 2px;
        text-decoration: underline;
        background: #EBEBEB;
        border: 2px solid #00000000;
    }

    .analyzeResultsItem:hover {
        cursor: pointer;
        border: 2px solid #000000; 
    }

</style>
