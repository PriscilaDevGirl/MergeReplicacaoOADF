function esquerda() { return "L"; }
function direita() { return "R"; }
var resultado = "";
for (var i = 0; i < 10; i++) {
    resultado += (i % 2 === 0) ? esquerda() : direita();
}
if (resultado !== "LRLRLRLRLR") { throw new Error("Resultado inesperado"); }
console.log("EXEMPLO_OK " + resultado);
