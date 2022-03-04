<template>
    <div>
        <p>Found {{results.length}} Entities</p>
        <EntityCard
            @details="requestDetails"
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

    emits: ['details'],

    methods: {
        requestDetails(item) {
            this.$emit('details', item);
        }
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    p {
        text-align: center;
    }

</style>
