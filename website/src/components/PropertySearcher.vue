<template>
    <div class="propertyfield">
        <h3>Search semantic Properties</h3> <!--<span class="arrow">→</span>-->
        <p class="arrow">🡺</p>
        <label for="selectfield">Search via semantic class:</label>
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
    name: 'PropertySearcher',
    components: {

    },
    expose: ['getData',],

    props: {
        classes: Array
    },

    data() {
        return {
            searchClass:  ''
        }
    },

    methods: {
        getData() {
            return {
                'searchClass': this.searchClass
            }
        }
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .propertyfield {
        display: flex;
        height: auto;
    }
    .arrow {
        font-size: 200%;
        margin: 1ex;
    }

    .selectfield {
        box-sizing: border-box;
        width: 90%;
        font-size: 1.2em;
        font-family: inherit;
        margin: 0.3em;
        color: inherit;
        align-self: flex-end;

    }
    .selectfield:hover {
        cursor: pointer;
    }
    .selectoption:hover {
        cursor: pointer;
    }

</style>
