"use client"

import { useState } from "react"
import { Download, Search, Trash2, UserX } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

type LogEntry = {
  id: string
  timestamp: Date
  user: string
  email: string
  query: string
  response: string
  documentId: string
  documentName: string
}

type User = {
  id: string
  name: string
  email: string
  status: "active" | "banned"
  plan: "free" | "pro"
  queries: number
  documents: number
  lastActive: Date
}

export default function AdminPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  // Sample log data
  const logs: LogEntry[] = [
    {
      id: "1",
      timestamp: new Date(2025, 2, 25, 14, 30),
      user: "John Doe",
      email: "john@example.com",
      query: "How do I calibrate the sensor?",
      response:
        "According to the technical manual, you should calibrate the sensor by following these steps: 1) Power off the device, 2) Press and hold the reset button for 5 seconds, 3) Power on while still holding the button, 4) Release when the LED flashes green.",
      documentId: "1",
      documentName: "Technical Manual v2.3.pdf",
    },
    {
      id: "2",
      timestamp: new Date(2025, 2, 25, 12, 15),
      user: "Jane Smith",
      email: "jane@example.com",
      query: "What's the maintenance schedule?",
      response:
        "The maintenance schedule in the field guide recommends servicing the equipment every 3 months under normal conditions, or monthly in high-dust environments.",
      documentId: "2",
      documentName: "Field Guide 2025.pdf",
    },
    {
      id: "3",
      timestamp: new Date(2025, 2, 24, 9, 45),
      user: "Mike Johnson",
      email: "mike@example.com",
      query: "Error code E-45 troubleshooting",
      response:
        "Error code E-45 indicates a power supply issue. Check the input voltage and ensure it's within the specified range of 110-240V. If the voltage is correct, the internal power module may need replacement.",
      documentId: "1",
      documentName: "Technical Manual v2.3.pdf",
    },
    {
      id: "4",
      timestamp: new Date(2025, 2, 23, 16, 20),
      user: "Sarah Williams",
      email: "sarah@example.com",
      query: "Power requirements for model X-200",
      response:
        "The technical specifications indicate that the Model X-200 requires a 24V DC power supply with at least 2.5A current capacity. Always use the manufacturer-approved power adapter.",
      documentId: "3",
      documentName: "Equipment Specs.pdf",
    },
    {
      id: "5",
      timestamp: new Date(2025, 2, 22, 11, 10),
      user: "John Doe",
      email: "john@example.com",
      query: "How to replace the filter?",
      response:
        "To replace the filter, follow these steps from the technical manual: 1) Turn off the power, 2) Remove the front panel by unscrewing the 4 screws, 3) Slide out the old filter, 4) Insert the new filter with the arrow pointing in the direction of airflow, 5) Replace the panel and secure with screws.",
      documentId: "1",
      documentName: "Technical Manual v2.3.pdf",
    },
  ]

  // Sample user data
  const users: User[] = [
    {
      id: "1",
      name: "John Doe",
      email: "john@example.com",
      status: "active",
      plan: "free",
      queries: 28,
      documents: 2,
      lastActive: new Date(2025, 2, 25, 14, 30),
    },
    {
      id: "2",
      name: "Jane Smith",
      email: "jane@example.com",
      status: "active",
      plan: "pro",
      queries: 156,
      documents: 8,
      lastActive: new Date(2025, 2, 25, 12, 15),
    },
    {
      id: "3",
      name: "Mike Johnson",
      email: "mike@example.com",
      status: "active",
      plan: "free",
      queries: 42,
      documents: 3,
      lastActive: new Date(2025, 2, 24, 9, 45),
    },
    {
      id: "4",
      name: "Sarah Williams",
      email: "sarah@example.com",
      status: "banned",
      plan: "pro",
      queries: 87,
      documents: 5,
      lastActive: new Date(2025, 2, 23, 16, 20),
    },
  ]

  const filteredLogs = logs.filter(
    (log) =>
      log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.response.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.documentName.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const filteredUsers = users.filter(
    (user) =>
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()),
  )

  const handleUserAction = (user: User) => {
    setSelectedUser(user)
    setIsDialogOpen(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Admin Dashboard</h2>
          <p className="text-muted-foreground">Manage users and view system logs</p>
        </div>
        <Button variant="outline" className="gap-2">
          <Download className="h-4 w-4" />
          Export Logs
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search logs and users..."
            className="pl-8"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <Tabs defaultValue="logs">
        <TabsList>
          <TabsTrigger value="logs">Audit Logs</TabsTrigger>
          <TabsTrigger value="users">User Management</TabsTrigger>
        </TabsList>

        <TabsContent value="logs" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Audit Logs</CardTitle>
              <CardDescription>Complete history of user queries and AI responses</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Timestamp</TableHead>
                      <TableHead>User</TableHead>
                      <TableHead>Query</TableHead>
                      <TableHead>Document</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredLogs.map((log) => (
                      <TableRow key={log.id}>
                        <TableCell className="font-medium">{log.timestamp.toLocaleString()}</TableCell>
                        <TableCell>
                          <div className="font-medium">{log.user}</div>
                          <div className="text-sm text-muted-foreground">{log.email}</div>
                        </TableCell>
                        <TableCell className="max-w-[300px] truncate">{log.query}</TableCell>
                        <TableCell>{log.documentName}</TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="icon">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>User Management</CardTitle>
              <CardDescription>Manage user accounts and permissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>User</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Plan</TableHead>
                      <TableHead>Usage</TableHead>
                      <TableHead>Last Active</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredUsers.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell>
                          <div className="font-medium">{user.name}</div>
                          <div className="text-sm text-muted-foreground">{user.email}</div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={user.status === "active" ? "outline" : "destructive"}>{user.status}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={user.plan === "pro" ? "default" : "secondary"}>{user.plan}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">{user.queries} queries</div>
                          <div className="text-sm text-muted-foreground">{user.documents} documents</div>
                        </TableCell>
                        <TableCell>{user.lastActive.toLocaleDateString()}</TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="icon" onClick={() => handleUserAction(user)}>
                            <UserX className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>User Actions</DialogTitle>
            <DialogDescription>Manage user account for {selectedUser?.name}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-2">
              <Label htmlFor="status">Account Status</Label>
              <Select defaultValue={selectedUser?.status}>
                <SelectTrigger id="status">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="banned">Banned</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="plan">Subscription Plan</Label>
              <Select defaultValue={selectedUser?.plan}>
                <SelectTrigger id="plan">
                  <SelectValue placeholder="Select plan" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="free">Free</SelectItem>
                  <SelectItem value="pro">Pro</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="action">Additional Actions</Label>
              <Select>
                <SelectTrigger id="action">
                  <SelectValue placeholder="Select action" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="reset">Reset Password</SelectItem>
                  <SelectItem value="delete">Delete Account</SelectItem>
                  <SelectItem value="export">Export User Data</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsDialogOpen(false)}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

