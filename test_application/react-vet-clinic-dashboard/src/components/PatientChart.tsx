// src/components/PatientChart.tsx
import { usePatientStore } from '../store';
import { Typography, Paper, Box } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';

type ChartData = {
  month: string;
  count: number;
};

export default function PatientChart() {
  const patients = usePatientStore(state => state.patients);

  const data: ChartData[] = [];
  const counts: { [key: string]: number } = {};

  patients.forEach(patient => {
    const date = new Date(patient.date);
    const month = date.toLocaleString('default', {
      month: 'short',
      year: 'numeric',
    });
    counts[month] = (counts[month] || 0) + 1;
  });

  const sortedMonths = Object.keys(counts).sort((a, b) => {
    const [monthA, yearA] = a.split(' ');
    const [monthB, yearB] = b.split(' ');
    const dateA = new Date(`${monthA} 1, ${yearA}`);
    const dateB = new Date(`${monthB} 1, ${yearB}`);
    return dateA.getTime() - dateB.getTime();
  });

  sortedMonths.forEach(month => {
    data.push({ month, count: counts[month] });
  });

  return (
    <Box sx={{ mt: 5 }}>
      <Typography variant='h5' align='center' gutterBottom>
        Patients Registered per Month
      </Typography>
      <Paper sx={{ p: 3 }}>
        {data.length > 0 ? (
          <ResponsiveContainer width='100%' height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray='3 3' />
              <XAxis dataKey='month' />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey='count' fill='#3f51b5' />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <Typography variant='body1' align='center'>
            No data to display.
          </Typography>
        )}
      </Paper>
    </Box>
  );
}
