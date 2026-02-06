// src/components/PatientsList.tsx
import { useState } from 'react';
import { usePatientStore } from '../store';
import PatientDetails from './PatientDetails';
import { Container, Typography, TextField, Box } from '@mui/material';

export default function PatientsList() {
  const patients = usePatientStore(state => state.patients);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredPatients = patients.filter(
    patient =>
      patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.caretaker.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Container sx={{ mt: 4 }}>
      <Typography variant='h3' align='center' gutterBottom>
        Patient List
      </Typography>
      <Typography variant='h5' align='center' gutterBottom>
        Manage your{' '}
        <span style={{ color: '#3f51b5', fontWeight: 'bold' }}>
          Patients and Appointments
        </span>
      </Typography>
      <Box sx={{ mb: 2 }}>
        <TextField
          label='Search patient...'
          variant='outlined'
          fullWidth
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </Box>
      {filteredPatients.length > 0 ? (
        filteredPatients.map(patient => (
          <PatientDetails key={patient.id} patient={patient} />
        ))
      ) : (
        <Typography variant='h6' align='center'>
          No patients found
        </Typography>
      )}
    </Container>
  );
}
