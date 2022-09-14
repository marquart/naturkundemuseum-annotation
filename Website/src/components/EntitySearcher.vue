<template>
    <div class="searcher">
        <h3>Search semantic Entities</h3>

        <div class="searchbox largebox">
            <label class="floatLeft" for="searchfield">
                Search an annotated word:
            </label>
            <input
                id="searchfield"
                placeholder="Please enter search term "
                v-model="searchString"
                type="text"
                @keydown.enter="search" />
        </div>

        <div v-if="props.moreSearchOptions" class="whiteBlock">
            <p class="bttn" @click="advancedSearchOpen = !advancedSearchOpen">
                {{ advancedSearchOpen ? '🡻' : '🡺' }} Search options
            </p>

            <div v-show="advancedSearchOpen" id="advancedSearch">
                <div class="searchbox smallbox">
                    <label class="floatLeft" for="selectfield">
                        Filter semantic class:
                    </label>
                    <select id="selectfield" v-model="searchClass">
                        <option selected value=""></option>
                        <option
                            class="selectoption"
                            v-for="(classString, i) in entityClasses"
                            :key="i"
                            :value="classString.slice(0, 4)">
                            {{ classString }}
                        </option>
                    </select>
                </div>

                <div class="searchbox minibox">
                    <label class="floatLeft" for="selectfieldDepth">
                        Set max results:*
                    </label>
                    <select id="selectfieldDepth" v-model="maxSize">
                        <option selected value="40">40</option>
                        <option
                            class="selectoption"
                            v-for="i in [60, 80, 100, 120, 140, 160, 180, 200]"
                            :key="i"
                            :value="i">
                            {{ i }}
                        </option>
                    </select>
                </div>
                <p>
                    * High values may negatively affect the performance on your
                    end.
                </p>
            </div>
        </div>
        <input type="submit" value="Search" id="button" @click="search" />
    </div>
</template>

<script setup>
    import { useDataStore } from '@/stores/data';
    import { ref } from 'vue';
    import { useRouter } from 'vue-router';
    import { storeToRefs } from 'pinia';

    const props = defineProps({
        route: String,
        moreSearchOptions: Boolean,
        params: Object,
    });

    const router = useRouter();
    const { entityClasses } = storeToRefs(useDataStore());

    const advancedSearchOpen = ref(false);
    const searchString = ref('');
    const searchClass = ref('');
    const maxSize = ref(40);

    function search() {
        router.push({
            name: props.route,
            params: props.params,
            query: {
                q: searchString.value.replace(/[ -]/g, '').toLowerCase(),
                class: searchClass.value,
                size: maxSize.value,
            },
        });
    }
</script>

<style scoped>
    .searcher {
        text-align: center;
        width: 80%;
        margin-left: 10%;
    }

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
        border: 1px solid #fff0;
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

    #button {
        box-sizing: border-box;
        display: inline;
        font-size: 1.2em;
        margin: 1.2em;
        font-family: inherit;
        color: inherit;
        cursor: pointer;
        text-align: center;
        width: 40%;
        background: #ffffff;
        margin-left: 0;
        border: 1px solid #2c3e50;
    }

    #button:hover {
        background: #ebebeb;
    }

    @media screen and (max-width: 1000px) {
        .searchbox {
            display: block;
        }

        .searcher {
            width: 100%;
            margin: 0%;
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
