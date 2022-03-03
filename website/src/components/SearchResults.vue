<template>
    <div>
        <p>Found {{results.length}} Entities</p>
        <EntityCard
            v-for="(result, i) in results"
            :key="i"
            :entity="result"
        />
    </div>
</template>

<script>
import EntityCard from './EntityCard.vue'

export default {
    name: 'SearchResults',
    components: {
        EntityCard
    },
    props: {
        results: Array
    },
    data() {
        return {
            
        }
    },

    methods: {
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    p {
        text-align: center;
    }

</style>
