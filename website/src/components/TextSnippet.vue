<template>
    <div class="text">
        <div class="textTable">
            <template
                v-for="(str, i) in linesBefore"
                :key="i" >
                <p class="linenumber">{{pageline-snippetSize+i}}</p>
                <p>{{str}}</p>
            </template>

            <p class="linenumber">{{pageline}}</p>
            <p class="highlightLine">{{line}}</p>

            <template
                v-for="(str, i) in linesAfter"
                :key="i" >
                <p class="linenumber">{{pageline+i+1}}</p>
                <p>{{str}}</p>
            </template>
        </div>
    </div>
</template>

<script>
export default {
    name: 'TextSnippet',
    props: {
        texts: Object,
        textidx: String,
        lineidx: Number,
        pageline: Number // Line number in Page
    },
    data()  {
        return {
            linesBefore: [],
            line: "",
            linesAfter: [],
            snippetSize: 10,

        }
    },

    mounted() {
        let text = this.texts[this.textidx];

        let beforeIdx = this.lineidx - this.snippetSize;
        let afterIdx  = this.lineidx + this.snippetSize;
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
        display: inline;
    }

    .textTable {
        display: grid;
        grid-template-columns: auto auto;
    }

    .linenumber {
        font-size: small;
    }
</style>
