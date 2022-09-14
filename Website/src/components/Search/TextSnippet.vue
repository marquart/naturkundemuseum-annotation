<template>
    <div class="text">
        <h2>Text Snippet</h2>
        <div class="textTable">
            <template v-for="(str, i) in linesBefore" :key="i">
                <p class="textLine linenumber">
                    {{ props.pageline - snippetSize + i }}
                </p>
                <p class="textLine">{{ str }}</p>
            </template>

            <p v-show="contentPresent" class="textLine linenumber">
                {{ props.pageline }}
            </p>
            <p class="textLine highlightLine">{{ line }}</p>

            <template v-for="(str, i) in linesAfter" :key="i">
                <p class="textLine linenumber">{{ props.pageline + i + 1 }}</p>
                <p class="textLine">{{ str }}</p>
            </template>
        </div>
    </div>
</template>

<script setup>
    import { useDataStore } from '@/stores/data';
    import { storeToRefs } from 'pinia';
    import { ref, onMounted } from 'vue';

    const { texts } = storeToRefs(useDataStore());
    const props = defineProps({
        textidx: String,
        lineidx: Number,
        pageline: Number, // Line number in Page
    });

    const linesBefore = ref([]),
        line = ref(''),
        linesAfter = ref([]),
        snippetSize = 6,
        contentPresent = ref(true);

    function buildText() {
        if (props.pageline < 0) {
            line.value = 'Artificially generated metadata';
            contentPresent.value = false;
        } else {
            const text = texts.value[props.textidx];

            let beforeIdx = props.lineidx - snippetSize;
            let afterIdx = props.lineidx + snippetSize + 1;
            if (beforeIdx < 0) beforeIdx = 0;
            if (afterIdx >= text.length) afterIdx = text.length - 1;

            linesBefore.value = text.slice(beforeIdx, props.lineidx);
            line.value = text[props.lineidx];
            linesAfter.value = text.slice(props.lineidx + 1, afterIdx);
            contentPresent.value = true;
        }
    }

    onMounted(buildText);
</script>

<style scoped>
    .text {
        text-align: justify;
        padding-left: 5%;
        padding-right: 5%;
        /*background: #EBEBEB;*/
    }

    .highlightLine {
        color: red;
        display: inline;
    }

    .textTable {
        display: grid;
        grid-template-columns: auto auto;
    }

    .linenumber {
        font-size: small;
    }

    .textLine {
        margin-top: 1ex;
        margin-bottom: 1ex;
    }
</style>
