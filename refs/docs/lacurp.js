$('#txtNombre').keyup(function () {
  this.value = this.value.toUpperCase();
});

$('#txtApellidoPaterno').keyup(function () {
  this.value = this.value.toUpperCase();
});

$('#txtApellidoMaterno').keyup(function () {
  this.value = this.value.toUpperCase();
});

function generar_pdf() {
  var doc = new jsPDF();
  var specialElementHandlers = {
    '#editor': function (element, renderer) { return true; }
  };
  doc.fromHTML( $('#container_curp').html(), 30, 30, 
      { 'width': 500, 'elementHandlers': specialElementHandlers } );
  doc.save('CURP.pdf');
}

function obtenerCURP() {
  var curp;
  var nombre = document.getElementById('txtNombre').value;
  var apellidoPaterno = document.getElementById('txtApellidoPaterno').value;
  var apellidoMaterno = document.getElementById('txtApellidoMaterno').value;
  var fecha = document.getElementById('txtFecha').value;
  var genero = document.getElementById('selGenero').value;
  var entidad = document.getElementById('selEntidad').value;
  var fecha_array = fecha.split('-');
  var fecha_nueva = fecha_array[2] + '/' + fecha_array[1] + '/' + fecha_array[0];
  var error = 0;
  if (!validaNombre(nombre)) {
    if (nombre == '') {
      alert('Escribe tu nombre por favor');
      error = 1;
    } else {
      alert('El campo nombre solo acepta letras (A-Z), el espacio y el punto. No se aceptan caracteres acentuados ni dieresis.');
      error = 1;
    }
  }
  if (!validaNombre(apellidoPaterno)) {
    if (apellidoPaterno == '') {
      alert('Escribe tu apellido paterno por favor. Si solo tienes un apellido, escribelo aquí.');
      error = 1;
    } else {
      alert('El campo de apellido paterno solo acepta letras (A-Z), el espacio y el punto. No se aceptan caracteres acentuados ni dieresis.');
      error = 1;
    }
  }
  if (!validaNombre(apellidoMaterno)) {
    if (apellidoMaterno != '') {
      alert('El campo apellido materno solo acepta letras (A-Z), el espacio y el punto. No se aceptan caracteres acentuados ni dieresis.');
      error = 1;
    }
  }
  if (fecha == '') {
    alert('Debes elegir tu fecha de nacimiento.');
    error = 1;
  }
  if (genero == 'x') {
    alert('Selecciona tu genero.');
    error = 1;
  }
  if (entidad == 'x') {
    alert('Elije tu lugar de nacimiento.');
    error = 1;
  }
  if (error == 0) {
    curp = GeneraCURP(nombre, apellidoPaterno, apellidoMaterno, fecha_nueva, genero, entidad);
    jQuery('#txtCURP').val(curp);
    jQuery('#nombre_curp').html(nombre);
    jQuery('#apellido_pat_curp').html(apellidoPaterno);
    jQuery('#apellido_mat_curp').html(apellidoMaterno);
    jQuery('#fecha_nac_curp').html(fecha_nueva);
    jQuery('#genero_curp').html(document.getElementById('selGenero').options[document.getElementById('selGenero').selectedIndex].text);
    jQuery('#entidad_nac_curp').html(document.getElementById('selEntidad').options[document.getElementById('selEntidad').selectedIndex].text);
    jQuery('#curpGenerado').html(curp);
    jQuery('#btn_generar_pdf').removeAttr('disabled');
    jQuery('#btn_generar_pdf').removeClass('disabled_btn');
  }
}

function GeneraCURP(nom, pat, mat, fecha, genero, edo) {
  var quitar, nombres, curp;
  nom = nom.toUpperCase();
  pat = pat.toUpperCase();
  mat = mat.toUpperCase();
  genero = genero.toUpperCase();
  quitar = new RegExp(/^(DE |DEL |LO |LOS |LA |LAS )+/);
  nombres = new RegExp(/^(MARIA |JOSE )/);
  nom = nom.replace(quitar, '');
  nom = nom.replace(nombres, '');
  nom = nom.replace(quitar, '');
  pat = pat.replace(quitar, '');
  mat = mat.replace(quitar, '');
  if (mat == '') mat = 'X';
  curp = pat.substring(0, 1) + buscaVocal(pat) + mat.substring(0, 1) + nom.substring(0, 2);
  curp = cambiaPalabra(curp);
  curp += fecha.substring(8, 10) + fecha.substring(3, 5) + fecha.substring(0, 2);
  curp += (genero == 'M' ? 'H' : 'M') + estado(edo);
  curp += buscaConsonante(pat) + buscaConsonante(mat) + buscaConsonante(nom);
  curp += fecha.substring(6, 8) == '19' ? '0' : 'A';
  curp += ultdig(curp);
  return curp;
}

function validaNombre(cmp) {
  var c, i;
  if (cmp.length == 0) return false;
  for (i = 0; i < cmp.length; i++) {
    c = cmp.charAt(i);
    if (!(('A' <= c && c <= 'Z') || c == 'Ã‘' || c == '.' || c == ' ')) return false;
  }
  return true;
}
function buscaVocal(str) {
  var vocales = 'AEIOU';
  var i, c;
  for (i = 1; i < str.length; i++) {
      c = str.charAt(i);
    if (vocales.indexOf(c) >= 0) {
      return c;
    }
  }
  return 'X';
}
function buscaConsonante(str) {
  var vocales = 'AEIOU Ññ.';
  var i, c;
  for (i = 1; i < str.length; i++) {
      c = str.charAt(i);
    if (vocales.indexOf(c) < 0) { return c; }
  }
  return 'X';
}
function cambiaPalabra(str) {
  var pal1 = new RegExp(/BUEI|BUEY|CACA|CACO|CAGA|CAGO|CAKA|CAKO|COGE|COJA|COJE|COJI|COJO|CULO|FETO|GUEY/);
  var pal2 = new RegExp(/JOTO|KACA|KACO|KAGA|KAGO|KOGE|KOJO|KAKA|KULO|LOCA|LOCO|MAME|MAMO|MEAR|MEAS|MEON/);
  var pal3 = new RegExp(/MION|MOCO|MULA|PEDA|PEDO|PENE|PUTA|PUTO|QULO|RATA|RUIN/);
  var val;
  str = str.substring(0, 4);
  val = pal1.test(str) || pal2.test(str);
  val = pal3.test(str) || val;
  if (val) return str.substring(0, 1) + 'X' + str.substring(2, 4);
  return str;
}
function estado(edo) {
  var edo;
  var vestado = new Array('DF', 'AS', 'BC', 'BS', 'CC', 'CL', 'CM', 'CS', 'CH', 'DG', 'GT', 'GR', 'HG', 'JC', 'MC', 'MN', 'MS', 'NT', 'NL', 'OC', 'PL', 'QT', 'QR', 'SP', 'SL', 'SR', 'TC', 'TS', 'TL', 'VZ', 'YN', 'ZS', 'NE');
  return vestado[edo];
}
function tabla(i, x) {
  if (i >= '0' && i <= '9') return x - 48;
  else if (i >= 'A' && i <= 'N') return x - 55;
  else if (i >= 'O' && i <= 'Z') return x - 54;
  else return 0;
}
function ultdig(curp) {
  var i, c, dv = 0;
  for (i = 0; i < curp.length; i++) {
    c = tabla(curp.charAt(i), curp.charCodeAt(i));
    dv += c * (18 - i);
  }
  dv %= 10;
  return dv == 0 ? 0 : 10 - dv;
}