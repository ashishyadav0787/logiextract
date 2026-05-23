import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const extractDocument = async (file) => {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/extract', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const validateAgainstPO = async (recordId, poFile) => {
  const form = new FormData()
  form.append('po_file', poFile)
  const { data } = await api.post(`/validate/${recordId}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}

export const getRecords = async (docType = null) => {
  const params = docType ? { doc_type: docType } : {}
  const { data } = await api.get('/records', { params })
  return data
}

export const getRecord = async (id) => {
  const { data } = await api.get(`/records/${id}`)
  return data
}

export const deleteRecord = async (id) => {
  await api.delete(`/records/${id}`)
}
