<template>
    <div>
  <p>{{ name }}(TNVC): </p>
  <form v-on:submit.prevent="">
    <label :for="typeCurr">type:</label>
    <select id="typeCurr" v-model="typeCurr">
         <option v-for="option in types"  v-bind:key="option" v-bind:value="option">
            {{ option }}
        </option>
    </select>
        <br>
    <label :for="nameCurr"> name:</label>
    <input :id="nameCurr" type="text" v-model="nameCurr"><br>
    <label :for="nameCurr">value:</label>
    <input :id="value" type="text" v-model="value"><br>
    <b-button type="submit" @click="addNewTnvc(typeCurr,nameCurr,value)">Add tnvc</b-button>
    <b-button type="submit" @click="deleteTnvc('a')">Remove tnvc</b-button>
  </form>
 
<label>
    Current TNVC:
{{result}} 
</label>

</div>
</template>

<script>

 export default {
   props: ["name","type","types","index"],
   data() {
    return {
    typeCurr:'',
    nameCurr:'',
    value:'',
    message: 'TNVC:',
    result:[],
    final:{"index": this.index,"type":"TNVC", "value":[]}
    
    }
  },
  methods: {
    addNewTnvc(t,n,v){
      t = t.trim();
      n = n.trim();
      v = v.trim();
    if( v == "" ){
          // only care about if the V in TNVC is used 
          // "value" overloaded term here means the value of the return object which would be an empty array
          this.final["value"] = this.result 
         this.$emit('updateResult', this.final)
    
    }else{ 
        var new_tnv =  v 
        this.result.push( new_tnv );
        this.final["value"] = this.result
        // every time a new  entry is added the final TNVC list is updated 
        this.$emit('updateResult', this.final)
    }
    },
    deleteTnvc(){
    this.result.pop()
       this.final["value"] = this.result
       this.$emit('updateResult', this.final)
    },
  }
}
</script>

<style>
.wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 100px 100px;
  gap: 10px;
}

</style>
