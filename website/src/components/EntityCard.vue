<template>
    <div class="card">
        <h4 class="typeHeading">{{entity.text}}</h4>
        <h5 class="entityText">{{entity.type}}</h5>
        <div class="numericTable">
            <div class="lcell">ID:</div>
            <div class="rcell">{{entity.id}}</div>

            <div class="lcell">Page:</div>
            <div class="rcell">{{entity.page}}</div>

            <div class="lcell">Line:</div>
            <div class="rcell">{{entity.line}}</div>
        </div>

        <h5>Incoming Relations</h5>
        <div class="propTable">
            <template
                v-for="(prop, i) in entity.incomingProps"
                :key="i">
                <div class="propItem">{{prop.source.type}}:</div>
                <div class="propItem">{{prop.source.text}}</div>
                <div class="propItem">→</div>
                <div class="propItem">{{prop.type}}</div>
                <div class="propItem">→</div>
            </template>
        </div>
        <h5>Outgoing Relations</h5>
        <div class="propTable">
            <template
                v-for="(prop, i) in entity.outgoingProps"
                :key="i">
                <div class="propItem">→</div>
                <div class="propItem">{{prop.type}}</div>
                <div class="propItem">→</div>
                <div class="propItem">{{prop.target.type}}:</div>
                <div class="propItem">{{prop.target.text}}</div>
            </template>
        </div>

    </div>
</template>

<script>

export default {
    name: 'EntityCard',
    components: {
    },
    props: {
        entity: Object
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
    .numericTable {
        display: grid;
        grid:
            'lcell rcell'
            'lcell rcell'
            'lcell rcell';
        width: 10%;
        margin-left: 46%;
    }

    .lcell {
        grid-area: 'lcell';
        display: block;
        text-align: left;
        margin: 5px;
    }

    .rcell {
        grid-area: 'rcell';
        display: block;
        text-align: left;
        margin: 5px;
    }

    .card {
        background: #ffffff;
        text-align: center;
        width: 80%;
        margin-left: 10%;
        margin-bottom: 1.5em;

    }

    .typeHeading {
        border-bottom: 1ex solid #f0f0f0;
        margin-bottom: 1px;
    }

    .entityText {
        margin: 3px;
        padding: 0;
    }

    .propTable {
        display: grid;
        grid-template-columns: auto auto auto auto auto;
    }

    .propItem {
        border: 1px solid #f0f0f0;
    }

</style>
