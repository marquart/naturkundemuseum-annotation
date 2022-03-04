<template>
    <div>
        <h3>Search semantic Entities</h3>
        <label for="searchfield">Search via an annotated word:</label>
        <input class="searchfield"
            placeholder="Please enter search term "
            v-model="searchString"
            type="text"
            @keydown.enter="$emit('query')"
        />

        <label for="selectfield">Search via an semantic class:</label>
        <select class="selectfield"
            v-model="searchClass">
            <option selected value=""></option>
            <option class="selectoption"
                v-for="(classString, i) in classes"
                :key="i"
                :value="classString.slice(0,4)"
            >
                {{classString}}
            </option>
        </select>
    </div>
</template>

<script>

export default {
    name: 'EntitySearcher',
    expose: ['getData',],
    components: {

    },

    props: {
        classes: Array
    },

    data() {
        return {
            searchString: '',
            searchClass:  ''
        }
    },

    methods: {
        getData() {
            return {
                'searchString': this.searchString,
                'searchClass': this.searchClass
            }
        },

    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .searchfield {
        box-sizing: border-box;
        width: 90%;
        font-size: 1.2em;
        font-family: inherit;
        margin: 1em;
        color: inherit;
    }
    .selectfield {
        box-sizing: border-box;
        width: 90%;
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
