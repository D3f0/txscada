function r(f){/loaded|complete/.test(document.readyState)?f():setTimeout("r("+f+")",9);}
function go() {
    var body = document.getElementsByTagName('body')[0];
    var e = document.createElement('p');
    e.setAttribute('class', 'cop');
    e.innerHTML =
    '<strong>Jornadas Regionales de Software Libre 2013</strong> | '
    + 'Defossé Nahuel (type <code>h</code> fort help)';
    body.appendChild(e);
}
r(go);