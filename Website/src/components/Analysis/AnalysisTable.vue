<template>
    <div class="analysisTable">
        <h3 class="entityClick person">{{ displayEntity[1] }}</h3>
        <p v-if="displayEntity[2].length > 1">
            Alternative names: {{ displayEntity[2].toString() }}
        </p>
        <!--<div
            class="yearGrid"
        >-->
        <p v-if="loading"><strong>Loading...</strong></p>
        <table v-else>
            <tr v-for="(yearData, i) in entityData[0]" :key="i" class="row">
                <!--Column1: Year-->
                <th class="item year">{{ years[i] }}</th>
                <!--Column2:-->
                <td>
                    <ul class="item">
                        <li
                            v-for="(lst, ii) in yearData"
                            :key="ii"
                            class="entityClick place"
                            :style="{
                                color: lst[2],
                                'font-size': lst[1] + 'px',
                            }"
                            @click="emitDisplayTextOf(lst[0])">
                            {{ entitiesMap[lst[0]].text }}
                            <!--{{entitiesMap[lst[0]].text}} ({{lst[1]}}x)-->
                        </li>
                    </ul>
                </td>
                <!--Column3:-->
                <td>
                    <ul class="item">
                        <li
                            v-for="(lst, ii) in entityData[1][i]"
                            :key="ii"
                            class="entityClick place"
                            :style="{
                                color: lst[2],
                                'font-size': lst[1] + 'px',
                            }"
                            @click="emitDisplayTextOf(lst[0])">
                            {{ entitiesMap[lst[0]].text }}
                            <!--{{entitiesMap[lst[0]].text}} ({{lst[1]}}x)-->
                        </li>
                    </ul>
                </td>
            </tr>
        </table>
    </div>
</template>

<script setup>
    import { storeToRefs } from 'pinia';
    import { useDataStore } from '@/stores/data';
    import { onBeforeMount, onMounted } from 'vue';
    import { useRouter } from 'vue-router';

    defineProps({
        displayEntity: Array,
        entityData: Array,
    });

    const { entitiesMap, loading } = storeToRefs(useDataStore());
    const router = useRouter();

    let years = [];

    function emitDisplayTextOf(entity_id) {
        router.push({ name: 'search', query: { id: entity_id } });
    }

    onBeforeMount(() => {
        for (let i = 1889; i < 1917; i++) {
            years.push(i);
        }
    });
</script>

<style scoped>
    .analysisTable {
        margin-left: 10%;
        margin-right: 10%;
        background: #fff;
        padding: 1em;
        border: 1px solid #ffffff;
        border-radius: 2px;
        box-shadow: 6px 6px #cbcbcb;
    }

    table {
        width: 100%;
    }

    table tr:nth-child(odd) {
        background-color: #f2f2f2;
    }

    table tr:nth-child(even) .entityClick {
        border: 3px solid #f2f2f2;
    }

    table tr:nth-child(odd) .entityClick {
        border: 3px solid #fff;
    }

    .item {
        margin: 2px;
    }

    .year {
        padding: 4px;
        border: 2px solid #00000000;
    }

    .entityClick {
        display: inline-block;
        padding: 4px;
        margin: 2px;

        background: #fff0; /*#EBEBEB;*/
    }

    .person {
        border: 3px solid #00000000;
    }

    .entityClick:hover {
        cursor: pointer;
        border: 3px solid #000000;
        text-decoration: underline;
    }
</style>
