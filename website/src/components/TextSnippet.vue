<template>
    <div class="text">
        <p  v-for="(str, i) in linesBefore"
            :key="i">
            {{i}} {{str}}
        </p>
        <p class="highlightLine">{{line}}</p>
        <p  v-for="(str, i) in linesAfter"
            :key="i">
            {{i}} {{str}}
        </p>
    </div>
</template>

<script>
export default {
    name: 'TextSnippet',
    props: {
        texts: Object,
        textidx: String,
        lineidx: Number
    },
    data()  {
        return {
            linesBefore: [],
            line: "",
            linesAfter: [],

        }
    },

    mounted() {
        let snippetSize = 10;
        let text = this.texts[this.textidx];

        let beforeIdx = this.lineidx - snippetSize;
        let afterIdx  = this.lineidx + snippetSize;
        if (beforeIdx < 0) beforeIdx = 0;
        if (afterIdx >= text.length) afterIdx = text.length-1;
            
        this.linesBefore = text.slice(beforeIdx, this.lineidx);
        this.line        = text[this.lineidx];
        this.linesAfter  = text.slice(this.lineidx+1, afterIdx);
    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .text {
        text-align: justify;
        padding-left: 5%;
        padding-right: 5%;
        background: #EBEBEB;
    }

    .highlightLine {
        color: red;
    }
</style>
