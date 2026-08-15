import client from './client'

// Backend returns a generated .docx file, so we request it as a blob
// and trigger a browser download.
export async function generateReport(payload) {
  const response = await client.post('/reports/generate', payload, {
    responseType: 'blob',
  })

  const disposition = response.headers['content-disposition']
  let filename = 'moneta-report.docx'
  if (disposition) {
    const match = disposition.match(/filename="?([^"]+)"?/)
    if (match) filename = match[1]
  }

  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
