// src/components/PatientDetailPage.tsx
import { useParams, useNavigate } from 'react-router-dom';
import { usePatientStore } from '../store';
import {
  Container,
  Typography,
  Paper,
  Button,
  Stack,
  Avatar,
  Box,
} from '@mui/material';
import PatientDetailItem from './PatientDetailItem';
import { toast } from 'react-toastify';

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const patients = usePatientStore(state => state.patients);
  const deletePatient = usePatientStore(state => state.deletePatient);
  const getPatientById = usePatientStore(state => state.getPatientById);

  const patient = patients.find(p => p.id === id);

  if (!patient) {
    return (
      <Typography variant='h6' align='center' sx={{ mt: 4 }}>
        Patient not found.
      </Typography>
    );
  }

  const handleEdit = () => {
    navigate('/');
    getPatientById(patient.id);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this patient?')) {
      deletePatient(patient.id);
      toast('Patient deleted', { type: 'error' });
      navigate('/');
    }
  };

  return (
    <Container maxWidth='sm' sx={{ mt: 4 }}>
      <Typography variant='h4' align='center' gutterBottom>
        Patient Details
      </Typography>
      <Paper sx={{ p: 3 }}>
        {patient.avatar && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Avatar
              src={patient.avatar}
              alt={patient.name}
              sx={{ width: 100, height: 100 }}
            />
          </Box>
        )}
        <PatientDetailItem label='ID' data={patient.id} />
        <PatientDetailItem label='Name' data={patient.name} />
        <PatientDetailItem label='Owner' data={patient.caretaker} />
        <PatientDetailItem label='Email' data={patient.email} />
        <PatientDetailItem
          label='Admission Date'
          data={new Date(patient.date).toLocaleDateString()}
        />
        <PatientDetailItem label='Symptoms' data={patient.symptoms} />

        <Stack
          direction='row'
          spacing={2}
          justifyContent='center'
          sx={{ mt: 3 }}
        >
          <Button variant='contained' color='primary' onClick={handleEdit}>
            Edit
          </Button>
          <Button variant='contained' color='error' onClick={handleDelete}>
            Delete
          </Button>
        </Stack>
      </Paper>
    </Container>
  );
}
