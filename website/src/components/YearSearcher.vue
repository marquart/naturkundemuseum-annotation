<template>
    <div class="selectContainer">
        <div class="griditem">
            <label for="selectfield"><h3>Search in year:</h3></label>
            <select class="selectfield"
                v-model="searchYear">
                <option selected value=0></option>
                <option class="selectoption"
                    v-for="(yearString, i) in years"
                    :key="i"
                    :value="parseInt(yearString.slice(0,4))"
                >
                    {{yearString}}
                </option>
            </select>
        </div>
        <div class="griditem">
            <label for="selectfield"><h3>Search in collection:</h3></label>
            <select class="selectfield"
                v-model="searchCollection">
                <option selected value=""></option>
                <option class="selectoption"
                    v-for="(collectionString, i) in collections"
                    :key="i"
                    :value="collectionString.slice(0,4)"
                >
                    {{collectionString}}
                </option>
            </select>
        </div>
    </div>
</template>

<script>
export default {
    name: 'YearSearcher',
    expose: ['getData',],
    props: {
        years: Array,
        collections: Array
    },

    data() {
      return {
        searchYear: 0,
        searchCollection: ''
      }
    },

    methods: {
        getData() {
            return {
                'searchYear': this.searchYear,
                'searchCollection': this.searchCollection
            }
        },

    },

}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .griditem {
        display: block;
        align-self: stretch;
        background: #ffffff;
        margin: 5px;
    }

    .selectContainer {
        display: grid;
        grid:
            auto auto;
        grid-auto-columns: minmax(0, 1fr);
        grid-auto-flow: column;
        text-align: center;
    }

    .selectfield {
        width: 80%;
        font-size: 1.2em;
        font-family: inherit;
        margin: 0.3em;
        color: inherit;
    }

    .selectfield:hover {
        cursor: pointer;
    }
    .selectoption:hover {
        cursor: pointer;
    }

</style>
