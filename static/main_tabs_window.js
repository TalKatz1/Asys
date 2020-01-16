function wait(ms) {
    var start = new Date().getTime();
    var end = start;
    while (end < start + ms) {
        end = new Date().getTime();
    }
}

function openPage(pageName, elmnt, color) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].style.backgroundColor = "";
    }
    document.getElementById(pageName).style.display = "block";
    elmnt.style.backgroundColor = color;
}
async function return_lap(lap_num) {
    const {
        value: user
    } = await Swal.fire({
        title: 'Who Are You?',
        input: 'select',
        inputOptions: {
            'Shai Michel Diner': 'Shai Michel Diner',
            'Tal Katz': 'Tal Katz',
            'Nimrod Hershkovitz': 'Nimrod Hershkovitz',
            'Noja Aldrich': 'Noja Aldrich',
            'Kosta Ruzin': 'Kosta Ruzin',
            'Tal Gonikman': 'Tal Gonikman',
            'Hofit Dahari': 'Hofit Dahari',
        },
        inputAttributes: {
            autocapitalize: 'off'
        },
        showCancelButton: true,
        cancelButtonColor: '#d33',
        confirmButtonText: 'OK',
    }).then((result) => {
        if (result.value) {
            $.ajax({
                method: 'POST',
                url: 'return_laptop_page',
                data: {
                    laptop: lap_num,
                    returned_by: result.value
                }
            })
            Swal.fire({
                icon: 'success',
                title: 'Thanks for returning the laptop!',
                showConfirmButton: false,
                timer: 1500
            })
            setTimeout(location.reload.bind(location), 1500);
        }
    })
}
async function ret_date_and_notes() {
    const {
        value: formValues
    } = await Swal.fire({
        title: 'Return Date & Notes',
        html: '<input id="return_date" input type="date" placeholder="Type the return date (dd.mm.yy) " class="swal2-input">'
        +
        '<input id="notes" placeholder="Type the notes (if you have any)" class="swal2-input">',
        focusConfirm: false,
        showCancelButton: true,
        cancelButtonColor: '#d33',
        preConfirm: () => {
            return {
                return_date: document.getElementById('return_date').value,
                notes: document.getElementById('notes').value
            }
        }
    })
    if (formValues) {
        Swal.fire({
            icon: 'success',
            title: 'Done!',
            showConfirmButton: false,
            timer: 1500
        })
    }
    return formValues;
}
async function loan_user() {
    const {
        value: user
    } = await Swal.fire({
        title: 'Who is the loaning user?',
        input: 'text',
        inputAttributes: {
            autocapitalize: 'off'
        },
        showCancelButton: true,
        inputPlaceholder: 'Enter the loaning user',
        cancelButtonColor: '#d33',
        confirmButtonText: 'OK',
    })
    return user
}
async function loan_lap(loan_lap_list) {
    var lap_num = loan_lap_list[0]
    var model = loan_lap_list[1]
    var serial_number = loan_lap_list[2]
    var userName = await loan_user();
    var {
        return_date,
        notes
    } = await ret_date_and_notes();
    $.ajax({
        method: 'POST',
        url: 'loan_laptop_page',
        data: {
            laptop: lap_num,
            model1: model,
            serial_number: serial_number,
            user: userName,
            return_date,
            notes
        }
    })
    setTimeout(location.reload.bind(location), 1500);
}