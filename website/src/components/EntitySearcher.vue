<template>
    <div>
        <h3>Search semantic Entities</h3>
        <!---->

        <!---->

        <div class="searchbox largebox">
            <label class="floatLeft" for="searchfield">Search an annotated word:</label>
            <input id="searchfield"
                placeholder="Please enter search term "
                v-model="searchString"
                type="text"
                @keydown.enter="$emit('query')"
            />
        </div>

        <div class="whiteBlock">
            <p class="bttn" @click="toggleAdvancedSearch">{{advancedSearchOpen ? '🡻': '🡺'}} Search options</p>

            <div v-show="advancedSearchOpen" id="advancedSearch">
                <div class="searchbox smallbox">
                <label class="floatLeft" for="selectfield">Filter semantic class:</label>
                <select id="selectfield"
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


                <div class="searchbox minibox">
                <label class="floatLeft" for="selectfield">Set max results:*</label>
                <select id="selectfieldDepth"
                    v-model="maxSize">
                    <option selected value=20>20</option>
                    <option class="selectoption"
                        v-for="i in [40,60,80,100,120,140,160,180,200]"
                        :key="i"
                        :value="i"
                    >
                        {{i}}
                    </option>
                </select>
                </div>
                <p>* High values will negatively affect the performance on your end.</p>
            </div>
        </div>

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
            advancedSearchOpen: false,
            searchString: '',
            searchClass:  '',
            maxSize: 20
        }
    },

    methods: {
        getData() {
            return {
                'searchString': this.searchString,
                'searchClass': this.searchClass,
                'maxSize': this.maxSize,
            }
        },

        toggleAdvancedSearch() {
            this.advancedSearchOpen = !this.advancedSearchOpen;
        },

    },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .searchbox {
        display: inline-block;
    }

    .largebox {
        width: 70%;
    }

    .smallbox {
        width: 60%;
    }

    .minibox {
        width: 20%;
    }

    #advancedSearch {
        width: 100%;
    }

    .bttn {
        text-align: left;
        color: #7da30b;
        border: 1px solid #FFF0;
        padding: 1ex;
    }

    .bttn:hover {
        cursor: pointer;
        border: 1px solid #7da30b;
    }

    #searchfield {
        font-family: inherit;
        color: inherit;
        display: block;
        font-size: x-large;
        width: 100%;
        box-sizing: border-box;
        margin-left: 1%;

        padding: 2px;
        border-radius: 0;
        border: none;
        outline: none;
        background-color: transparent;
        border-bottom: 1px solid #333333;
        color: #7da30b;
        /*
        box-sizing: border-box;
        width: 90%;
        font-size: 1.2em;
        margin: 0.3em;*/
    }

    #selectfield {
        font-family: inherit;
        color: inherit;
        display: block;
        font-size: large;
        width: 100%;
        box-sizing: border-box;


        
        padding: 2px;
        border-radius: 0;
        border: none;
        outline: none;
        background-color: transparent;
        border-bottom: 1px solid #333333;
        color: #7da30b;
        /*
        box-sizing: border-box;
        width: 90%;
        font-size: 1.2em;
        margin: 0.3em;*/
    }

    #selectfieldDepth {
        font-family: inherit;
        color: inherit;
        display: block;
        font-size: large;
        width: 100%;
        box-sizing: border-box;
        margin-left: 10%;
        
        padding: 2px;
        border-radius: 0;
        border: none;
        outline: none;
        background-color: transparent;
        border-bottom: 1px solid #333333;
        color: #7da30b;
    }

    #selectfield:hover {
        cursor: pointer;
    }
    #selectoption:hover {
        cursor: pointer;
    }
    #selectfieldDepth:hover {
        cursor: pointer;
    }

    label {
        display: inline-block;
    }

    .floatRight {
        float: right;
    }

    .floatLeft {
        float: left;
    }

    .whiteBlock {
        
        width: 70%;
        margin-left: 15%;
    }

    @media screen and (max-width: 1000px) {
        .searchbox  {
            display: block;
        }

        .largebox {
            width: 100%;
        }

        .smallbox {
            width: 100%;
        }

        .minibox {
            width: 100%;
            margin-left: 0%;
        }
    }
</style>
