<template>
    <div>
        <p>Found {{results.length}} Entities</p>
        <EntityCard
            @showOneEntity="showOneEntity"
            @displayGraphOf="emitDisplayGraphOf"
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

    emits: ['showOneEntity', 'displayGraphOf'],

    methods: {
        showOneEntity(item) {
            this.$emit('showOneEntity', item);
        },
        emitDisplayGraphOf(item_id) {
            this.$emit('displayGraphOf', item_id);
        },
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    p {
        text-align: center;
    }

</style>
