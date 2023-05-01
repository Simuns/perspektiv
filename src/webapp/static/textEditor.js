// LOAD DEPENDENCIES
const sources = [
  {
    type: 'script',
    src: 'https://code.jquery.com/jquery-3.6.0.min.js',
    check: 'jQuery'
  },
  {
    type: 'script',
    src: '/static/textEditor.js',
    check: 'Quill'
  },
  {
    type: 'link',
    rel: 'stylesheet',
    href: 'https://cdn.quilljs.com/1.3.6/quill.snow.css',
    check: 'Quill'
  }
];

for (let i = 0; i < sources.length; i++) {
  const source = sources[i];
  const existing = document.querySelector(`${source.type}[src="${source.src}"],${source.type}[href="${source.href}"]`);
  
  if (!existing) {
    const newSource = document.createElement(source.type);

    if (source.type === 'script') {
      newSource.src = source.src;
    } else if (source.type === 'link') {
      newSource.rel = source.rel;
      newSource.href = source.href;
    }

    if (source.check) {
      newSource.onload = () => {
        if (window[source.check]) {
          // Do something after script or stylesheet has loaded
        }
      };
    }

    document.head.appendChild(newSource);
  }
}


// Create the script element for Quill
const quillScript = document.createElement('script');
quillScript.src = 'https://cdn.quilljs.com/1.3.6/quill.js';

// Add an onload event listener to the Quill script
quillScript.onload = function() {
  // This code will run after Quill has finished loading
  const quill = new Quill('#editor', {
    modules: {
      toolbar: [
        ['bold', 'italic', 'underline'],
        [{ 'header': 2 }],
        [{ 'list': 'ordered' }, { 'list': 'bullet' }],
        [{ 'align': [] }],
        ['image'],
        ['clean']
      ]
    },
    theme: 'snow'
  });
  /*
  $('#skriva').submit(function(event) {
    var contents = quill.getContents();
    $('#hiddenArea').val($('#editor .ql-editor').html());
  });
  */
    $('.postButton').click(function(event) {
    event.preventDefault(); // prevent the form from submitting normally
    var contents = quill.getContents();
    $.ajax({
      url: '/ppost-grein',
      type: 'POST',
      data: { contents: contents },
      success: function(response) {
        // Do something if the post is successful
      },
      error: function(xhr) {
        // Do something if there is an error
      }
    });
  });
};

// Add the Quill script to the document head
document.head.appendChild(quillScript);



