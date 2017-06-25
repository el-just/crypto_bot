function toPrecision (firstValue, secondValue) {
   if (firstValue.exp > secondValue.exp) {
      secondValue.value = secondValue.value*Math.pow (10, firstValue.exp - secondValue.exp)
      secondValue.exp = firstValue.exp;
   }
   else if (firstValue.exp < secondValue.exp) {
      firstValue.value = firstValue.value*Math.pow (10, secondValue.exp - firstValue.exp)
      firstValue.exp = secondValue.exp;
   }
}

function ChartValue (value) {
   var
      currentPriceInteger = (value+'').split('.')[0],
      currentPriceFloat = (value+'').split('.')[1];

   this.value = parseInt(currentPriceInteger)*Math.pow(10, currentPriceFloat.length) + parseInt(currentPriceFloat);
   this.exp = currentPriceFloat.length;
   
   this.isMore = function (value) {
      if (value.exp !== this.exp) {
         if (value.exp > this.exp) {
            return Math.pow (10, value.exp - this.exp)*this.value > value.value;
         }
         else {
            return this.value > Math.pow (10, this.exp - value.exp)*value.value;
         }
      }
      else {
         return this.value > value.value;
      }
   }
   this.isLess = function (value) {
      if (value.exp !== this.exp) {
         if (value.exp > this.exp) {
            return Math.pow (10, value.exp - this.exp)*this.value < value.value;
         }
         else {
            return this.value < Math.pow (10, this.exp - value.exp)*value.value;
         }
      }
      else {
         return this.value < value.value;
      }
   }
   this.isEqual = function (value) {
      if (value.exp !== this.exp) {
         if (value.exp > this.exp) {
            return Math.pow (10, value.exp - this.exp)*this.value === value.value;
         }
         else {
            return this.value === Math.pow (10, this.exp - value.exp)*value.value;
         }
      }
      else {
         return this.value === value.value;
      }
   }
}

ChartValue.toPrecision = toPrecision;
module.exports = ChartValue;