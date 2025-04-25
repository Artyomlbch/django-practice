
var list = document.getElementById("filter");
function onChange() {
    var value = list.value;
    var text = list.options[list.selectedIndex].text;
    document.getElementById('filter_submit_button').style.display = '';

    console.log(value, text);

    if (value != "no_filter") {
        document.getElementById(value).style.display = '';
        if (value === 'name') {
            document.getElementById('author').style.display = 'none';
        } else if (value === 'author') {
            document.getElementById('name').style.display = 'none';
        }
    } else {
        document.getElementById('author').style.display = 'none';
        document.getElementById('name').style.display = 'none';
    }

}
list.onchange = onChange;

