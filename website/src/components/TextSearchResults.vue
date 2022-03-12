<template>
    <div>
        <p>Found {{results.length}} Entities</p>
        <TextEntityCard
            @showOneEntity="showOneEntity"
            @displayGraphOf="emitDisplayGraphOf"
            v-for="result in results"
            :key="result.id"
            :entity="result"
            :texts="texts"
        />
    </div>
</template>

<script>
import TextEntityCard from './TextEntityCard.vue'

export default {
    name: 'TextSearchResults',
    components: {
        TextEntityCard
    },
    props: {
        results: Array,
        texts: Object
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
