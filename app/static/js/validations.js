/**
 * Global Validations & Formatting
 * Centro Médico Integral
 */

// 1. Formatea un RUT plano a la vista (ej: 123456789 -> 12.345.678-9)
function formatoRutVisual(rutPlano) {
    if (!rutPlano) return "";
    let valor = rutPlano.replace(/[^0-9kK]/g, '').toUpperCase();
    if (valor.length > 1) {
        let cuerpo = valor.slice(0, -1);
        let dv = valor.slice(-1);
        return cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, ".") + "-" + dv;
    }
    return valor;
}

// 2. Valida matemáticamente un RUT plano (Módulo 11)
function validarRutMatematico(rutPlano) {
    if (!rutPlano || rutPlano.length < 2) return false;
    
    let c = rutPlano.slice(0, -1);
    let d = rutPlano.slice(-1);
    let s = 0;
    let m = 2;
    
    for (let i = 1; i <= c.length; i++) { 
        s += m * parseInt(c.charAt(c.length - i)); 
        m = m < 7 ? m + 1 : 2; 
    }
    
    let dv = 11 - (s % 11); 
    dv = (dv === 11) ? "0" : (dv === 10) ? "K" : dv.toString();
    
    return d === dv;
}

// 3. Aplica formato a todas las celdas de una grilla con la clase .formato-rut-cl
function formatearGrillaRuts() {
    document.querySelectorAll('.formato-rut-cl').forEach(td => {
        let v = td.innerText.replace(/[^0-9kK]/g, '').toUpperCase();
        if (v.length > 1) {
            td.innerText = formatoRutVisual(v);
        }
    });
}